from __future__ import annotations

import json
from typing import Dict, List, Optional, Tuple

from google.auth.transport import requests as google_auth_requests
from google.oauth2.credentials import Credentials
from google.oauth2.id_token import verify_oauth2_token
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from pydantic import BaseModel, validator

from app.core.config import settings
from app.models.user import User, UserCreate


class GoogleAPI(BaseModel):
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

    @validator("client_id")
    def prevent_none_client_id(cls, v: Optional[str]):
        return v or settings.OAUTH.CLIENT_ID

    @validator("client_secret")
    def prevent_none_client_secret(cls, v: Optional[str]):
        return v or settings.OAUTH.CLIENT_SECRET

    def get_auth_flow(
        self, redirect_uri: str, state: Optional[str] = None
    ) -> Flow:
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": settings.OAUTH.AUTH_URI,
                "token_uri": settings.OAUTH.TOKEN_URI,
            }
        }

        flow_parameters = {
            "client_config": client_config,
            "scopes": settings.OAUTH.SCOPES,
            "redirect_uri": redirect_uri,
        }

        if state is not None:
            flow_parameters["state"] = state

        return Flow.from_client_config(**flow_parameters)

    def get_auth_url_with_state(
        self, redirect_uri: str, state: Optional[str] = None
    ) -> Tuple[str, str]:

        flow = self.get_auth_flow(redirect_uri=redirect_uri, state=state)

        return flow.authorization_url(
            access_type=settings.OAUTH.ACCESS_TYPE,
            prompt=settings.OAUTH.PROMPT_TYPE,
        )

    def get_user_from_authcode(
        self, code: str, redirect_uri: str, state: Optional[str] = None
    ) -> UserCreate:
        gar = google_auth_requests.Request()

        flow = self.get_auth_flow(redirect_uri=redirect_uri, state=state)

        flow.fetch_token(code=code)
        credentials = flow.credentials

        identity = verify_oauth2_token(
            credentials.id_token, gar, audience=self.client_id
        )

        user = UserCreate(
            uid=identity["sub"],
            email=identity["email"],
            credentials=self.get_credentials_info(credentials=credentials),
        )

        return user

    @staticmethod
    def get_user_credentials_info(user: User) -> dict[str, str]:
        info: dict[str, str] = json.loads(user.credentials)

        if not "client_id" in info:
            info.update(
                {
                    "client_id": settings.OAUTH.CLIENT_ID,
                    "client_secret": settings.OAUTH.CLIENT_SECRET,
                }
            )

        return info

    @staticmethod
    def get_user_credentials(user: User) -> Credentials:
        info = GoogleAPI.get_user_credentials_info(user=user)
        credentials = Credentials.from_authorized_user_info(info=info)

        if not credentials.valid:
            gar = google_auth_requests.Request()
            # TODO: Find a way to save credentials after refresh
            credentials.refresh(gar)

        if credentials.valid:
            return credentials

        raise ValueError

    @staticmethod
    def get_credentials_info(credentials: Credentials) -> str:
        if credentials.client_id == settings.OAUTH.CLIENT_ID:
            return credentials.to_json(strip=["client_id", "client_secret"])
        else:
            return credentials.to_json()

    class Config:
        arbitrary_types_allowed = True


class GoogleUserAPI(GoogleAPI):
    user: User

    @classmethod
    def from_user(cls, user: User) -> "GoogleUserAPI":
        info = GoogleAPI.get_user_credentials_info(user=user)

        return GoogleUserAPI(
            client_id=info["client_id"],
            client_secret=info["client_secret"],
            user=user,
        )

    def get_profile(self) -> Dict[str, str]:
        credentials = self.get_user_credentials(user=self.user)

        with build("oauth2", "v2", credentials=credentials) as service:
            return service.userinfo().get().execute()

    def get_project_ids(self) -> List[Dict[str, str]]:
        credentials = self.get_user_credentials(user=self.user)

        with build(
            "cloudresourcemanager", "v1", credentials=credentials
        ) as service:
            filter = "lifecycleState:ACTIVE"
            projects_response = (
                service.projects().list(filter=filter).execute()
            )

            projects = [
                {"name": project["name"], "id": project["projectId"]}
                for project in projects_response["projects"]
            ]

            return projects

    class Config:
        arbitrary_types_allowed = True
