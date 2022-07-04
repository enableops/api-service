from typing import Dict, Optional

from fastapi import HTTPException, status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.param_functions import Cookie, Depends, Path
from fastapi.security.oauth2 import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.config import settings
from app.database.crud import user as crud
from app.main import SessionLocal
from app.models.exception import APIException
from app.models.token import TokenData
from app.models.user import User
from app.services.google_api import GoogleAPI, GoogleUserAPI


def decode(jwt_token: str):
    return jwt.decode(
        jwt_token,
        settings.SECURITY.SESSION_SIGN_KEY,
        algorithms=[settings.SECURITY.JWT_ALGORITHM],
    )


class OAuth2AuthorizationCodeBearerOrSession(OAuth2):
    def __init__(
        self,
        authorizationUrl: str,
        tokenUrl: str,
        refreshUrl: Optional[str] = None,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            authorizationCode={
                "authorizationUrl": authorizationUrl,
                "tokenUrl": tokenUrl,
                "refreshUrl": refreshUrl,
                "scopes": scopes,
            }
        )
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(
        self, request: Request, access_token: Optional[str] = Cookie(None)
    ) -> Optional[str]:
        no_auth_exception = HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer/CSFR"},
        )

        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        is_bearer = authorization is not None and scheme.lower() == "bearer"
        is_double_cookie = (
            authorization is not None
            and scheme.lower() == "csfr"
            and access_token is not None
        )

        valid_double_cookie = None
        if is_double_cookie:
            if access_token is None:
                raise no_auth_exception

            cookie_secret = decode(jwt_token=access_token).get("csrf_secret")
            token_secret = decode(jwt_token=param).get("csrf_secret")

            valid_double_cookie = (
                cookie_secret
                and token_secret
                and cookie_secret == token_secret
            )

        if not is_bearer and not valid_double_cookie:
            if self.auto_error:
                raise no_auth_exception
            else:
                return None  # pragma: nocover

        return access_token if valid_double_cookie else param


oauth2_scheme = OAuth2AuthorizationCodeBearerOrSession(
    authorizationUrl=(
        "/v1" f"{settings.PATH.AUTH_MODULE}" f"{settings.PATH.AUTH_REDIRECT}"
    ),
    tokenUrl=(
        "/v1" f"{settings.PATH.AUTH_MODULE}" f"{settings.PATH.AUTH_TOKEN}"
    ),
    auto_error=True,
)


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_gapi(
    client_id: Optional[str] = None, client_secret: Optional[str] = None
) -> GoogleAPI:
    return GoogleAPI(client_id=client_id, client_secret=client_secret)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode(jwt_token=token)
        uid: str = payload["sub"]
        if uid is None:
            raise credentials_exception
        token_data = TokenData(sub=uid)
        uid = token_data.sub
    except JWTError:
        raise credentials_exception

    db_user = crud.get_user(db=db, uid=uid)
    if db_user is None:
        raise credentials_exception

    return User.from_orm(db_user)


async def get_user_gapi(
    user: User = Depends(get_current_user),
) -> GoogleUserAPI:
    return GoogleUserAPI.from_user(user=user)


async def verify_users_api_access(
    user_uid: str = Path(
        "me", description="The 'uid' of user, or 'me' as alias to current user"
    ),
    user: User = Depends(get_current_user),
):
    if user_uid != "me" and user.uid != user_uid:
        raise APIException.NOTYOU403
