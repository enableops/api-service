from typing import Dict, Optional

from fastapi import HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.param_functions import Cookie
from fastapi.security.oauth2 import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED


from app import urls
from services import jwt


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

            token_service = jwt.get_jwt()

            cookie_secret = token_service.decode(jwt_token=access_token).get(
                "csrf_secret"
            )
            token_secret = token_service.decode(jwt_token=param).get(
                "csrf_secret"
            )

            valid_double_cookie = (
                cookie_secret and token_secret and cookie_secret == token_secret
            )

        if not is_bearer and not valid_double_cookie:
            if self.auto_error:
                raise no_auth_exception
            else:
                return None  # pragma: nocover

        return access_token if valid_double_cookie else param


oauth2_scheme = OAuth2AuthorizationCodeBearerOrSession(
    authorizationUrl=f"/v1{urls.Sections.auth}{urls.Auth.start}",
    tokenUrl=f"/v1{urls.Sections.auth}{urls.Auth.token}",
    auto_error=True,
)
