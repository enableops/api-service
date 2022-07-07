import logging
from typing import Dict
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import settings
from app import main
from app import oauth
from services import googleauth, jwt, googleapi

from app.database.crud import user as crud
from app.models.token import TokenData
from app.models.user import User

from google.auth.transport import requests as google_auth_requests
from google.oauth2.credentials import Credentials
from google.oauth2.id_token import verify_oauth2_token
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.discovery import build


async def get_db():
    db = main.SessionLocal()
    try:
        yield db
    finally:
        db.close()


get_oauth = lambda: googleauth.get_gauth()
get_token_service = lambda: jwt.get_jwt()
get_app_settings = lambda: settings.Settings().api


def get_current_user_credentials_json(
    token: str = Depends(oauth.oauth2_scheme),
    db: Session = Depends(get_db),
) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_service = jwt.get_jwt()
    try:
        payload = token_service.decode(jwt_token=token)
        uid: str = payload["sub"]
        if uid is None:
            raise credentials_exception
        token_data = TokenData(sub=uid)
        uid = token_data.sub
    except:
        raise credentials_exception

    db_user = crud.get_user(db=db, uid=uid)
    if db_user is None:
        raise credentials_exception

    credentials_json = str(db_user.credentials)

    return credentials_json


async def get_user_api(
    credentials_json: str = Depends(get_current_user_credentials_json),
) -> googleapi.GoogleUserAPI:
    user_api = googleapi.GoogleUserAPI.from_credentials_json(
        credentials_json=credentials_json
    )

    with build("oauth2", "v2", credentials=user_api.credentials) as service:
        user_info: Dict[str, str] = service.userinfo().get().execute()
        print(user_info)

    return user_api
