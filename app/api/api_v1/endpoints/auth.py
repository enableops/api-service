from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Request, Response
from fastapi.param_functions import Depends
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.database.crud import user as crud
from app.models.token import Token, TokenRequestForm

from app.models import urls
from app import protocols as protos
from app import dependencies as deps
from app import settings

router: APIRouter = APIRouter()


@router.get(urls.Auth.settings)
async def get_settings(oauth: protos.OAuth = Depends(deps.get_oauth)):
    return {
        "client_id": oauth.client_id,
        "prompt": oauth.prompt_type,
        "access_type": oauth.access_type,
        "scope": " ".join(oauth.scopes),
        "token_url": "/v1" + urls.Sections.auth + urls.Auth.token,
    }


@router.get(urls.Auth.start)
async def start_auth(
    request: Request,
    state: Optional[str] = None,
    oauth: protos.OAuth = Depends(deps.get_oauth),
    redirect_uri: Optional[str] = None,
    app_settings: settings.APISettings = Depends(deps.get_app_settings),
):
    if redirect_uri is None:
        redirect_uri = (
            f"{app_settings.host_url}/v1{urls.Sections.auth}{urls.Auth.token}"
        )

    auth_url, state = oauth.get_auth_url_with_state(
        redirect_uri=redirect_uri, state=state
    )

    request.session["state"] = state
    return RedirectResponse(url=auth_url)


@router.get(urls.Auth.logout)
async def logout_from_session(response: Response):
    cookie_delete = "access_token=; Max-Age=0; Path=/; SameSite=None; Secure"
    response.headers.update({"Set-Cookie": cookie_delete})
    return "Sorry to see you go"


@router.post(urls.Auth.token, response_model=Token)
def get_token(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    form: TokenRequestForm = Depends(),
    db: Session = Depends(deps.get_db),
    oauth: protos.OAuth = Depends(deps.get_oauth),
    token_service: protos.TokenService = Depends(deps.get_token_service),
):
    state = request.session.pop("state", None)

    user = oauth.get_user_from_authcode(
        code=form.code, state=state, redirect_uri=form.redirect_uri
    )
    background_tasks.add_task(crud.update_user, db=db, user=user)

    token = token_service.create_access_token(for_sub=user.uid)
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        path="/",
        secure=True,
        httponly=True,
        samesite="none",
    )

    return token
