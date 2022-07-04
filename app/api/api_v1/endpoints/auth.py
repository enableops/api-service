from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Request, Response
from fastapi.param_functions import Depends
from jose import jwt
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.api.dependencies import get_db, get_gapi
from app.core.config import settings
from app.database.crud import user as crud
from app.models.token import Token, TokenData, TokenRequestForm
from app.models.user import UserCreate
from app.services.google_api import GoogleAPI

router: APIRouter = APIRouter()


@router.get("/settings")
async def get_settings():
    return {
        "client_id": settings.OAUTH.CLIENT_ID,
        "prompt": settings.OAUTH.PROMPT_TYPE,
        "access_type": settings.OAUTH.ACCESS_TYPE,
        "scope": " ".join(settings.OAUTH.SCOPES),
        "token_url": (
            f"{settings.OAUTH.REDIRECT_HOST}/v1"
            f"{settings.PATH.AUTH_MODULE}"
            f"{settings.PATH.AUTH_TOKEN}"
        ),
    }


@router.get(settings.PATH.AUTH_REDIRECT)
async def start_auth(
    request: Request,
    redirect_uri: str = (
        f"{settings.OAUTH.REDIRECT_HOST}/v1"
        f"{settings.PATH.AUTH_MODULE}"
        f"{settings.PATH.AUTH_TOKEN}"
    ),
    state: Optional[str] = None,
    gapi: GoogleAPI = Depends(get_gapi),
):
    auth_url, state = gapi.get_auth_url_with_state(
        redirect_uri=redirect_uri, state=state
    )

    request.session["state"] = state
    return RedirectResponse(url=auth_url)


@router.get("/logout")
async def logout_from_session(response: Response):
    # TODO: Let starlette know about this bug
    cookie_delete = "access_token=; Max-Age=0; Path=/; SameSite=None; Secure"
    response.headers.update({"Set-Cookie": cookie_delete})
    return "Sorry to see you go"


@router.post(settings.PATH.AUTH_TOKEN, response_model=Token)
def get_token(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    form: TokenRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    gapi = get_gapi(client_id=form.client_id, client_secret=form.client_secret)

    state = request.session.pop("state", None)

    user = gapi.get_user_from_authcode(
        code=form.code, state=state, redirect_uri=form.redirect_uri
    )
    background_tasks.add_task(crud.update_user, db=db, user=user)

    token = create_access_token(user=user)
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        path="/",
        secure=True,
        httponly=True,
        samesite="none",
    )

    return token


def create_access_token(user: UserCreate) -> Token:
    token_expires = timedelta(
        minutes=settings.SECURITY.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    token_data = TokenData(sub=user.uid)
    access_token = generate_token(
        data=token_data.dict(), expires_delta=token_expires
    )
    csrf_token = generate_token(
        data={"csrf_secret": token_data.csrf_secret},
        expires_delta=token_expires,
    )

    return Token(
        access_token=access_token, csrf_token=csrf_token, token_type="bearer"
    )


def generate_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()

    expire_datetime = datetime.now() + expires_delta
    exp_timestamp = int(datetime.timestamp(expire_datetime))

    to_encode.update({"exp": exp_timestamp})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECURITY.SESSION_SIGN_KEY,
        algorithm=settings.SECURITY.JWT_ALGORITHM,
    )

    return encoded_jwt
