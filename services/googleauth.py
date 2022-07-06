from dataclasses import dataclass
import json
import os
from typing import Dict, List, Optional, Tuple

from google.auth.transport import requests as google_auth_requests
from google.oauth2.credentials import Credentials
from google.oauth2.id_token import verify_oauth2_token
from google_auth_oauthlib.flow import Flow

from pydantic import BaseModel, parse_obj_as


class OAuthSettings(BaseModel):
    CLIENT_ID: str = ""
    CLIENT_SECRET: str = ""
    AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URI: str = "https://accounts.google.com/o/oauth2/token"
    ACCESS_TYPE: str = "offline"
    PROMPT_TYPE: str = "consent"
    SCOPES: List[str] = []


class Settings(BaseModel):
    oauth: OAuthSettings

    class Config:
        env_nested_delimiter = "__"
        secrets_dir = os.getenv("SECRETS_PATH")


@dataclass
class GoogleOAuthUser:
    uid: str
    email: str
    credentials: str


class GoogleOAuth:
    client_id: str
    client_secret: str
    auth_uri: str
    token_uri: str
    scopes: List[str]
    access_type: str
    prompt_type: str

    def __init__(self, *, settings: Settings):
        self.client_id = settings.oauth.CLIENT_ID
        self.client_secret = settings.oauth.CLIENT_SECRET
        self.auth_uri = settings.oauth.AUTH_URI
        self.token_uri = settings.oauth.TOKEN_URI
        self.scopes = settings.oauth.SCOPES
        self.access_type = settings.oauth.ACCESS_TYPE
        self.prompt_type = settings.oauth.PROMPT_TYPE

    def get_auth_flow(
        self, redirect_uri: str, state: Optional[str] = None
    ) -> Flow:
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": self.auth_uri,
                "token_uri": self.token_uri,
            }
        }

        flow_parameters = {
            "client_config": client_config,
            "scopes": self.scopes,
            "redirect_uri": redirect_uri,
        }

        if state is not None:
            flow_parameters["state"] = state

        return Flow.from_client_config(**flow_parameters)

    def get_auth_url_with_state(
        self, *, redirect_uri: str, state: Optional[str] = None
    ) -> Tuple[str, str]:

        flow = self.get_auth_flow(redirect_uri=redirect_uri, state=state)

        auth_url, state = flow.authorization_url(
            access_type=self.access_type,
            prompt=self.prompt_type,
        )

        return (str(auth_url), str(state))

    def get_user_from_authcode(
        self, code: str, redirect_uri: str, state: str
    ) -> GoogleOAuthUser:
        gar = google_auth_requests.Request()

        flow = self.get_auth_flow(redirect_uri=redirect_uri, state=state)

        flow.fetch_token(code=code)
        credentials = flow.credentials

        identity = verify_oauth2_token(
            credentials.id_token, gar, audience=self.client_id
        )

        user = GoogleOAuthUser(
            uid=identity["sub"],
            email=identity["email"],
            credentials=self.get_credentials_info(credentials=credentials),
        )

        return user

    def get_user_credentials_info(
        self, user: GoogleOAuthUser
    ) -> dict[str, str]:
        info: dict[str, str] = json.loads(user.credentials)

        if not "client_id" in info:
            info.update(
                {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                }
            )

        return info

    def get_user_credentials(self, user: GoogleOAuthUser) -> Credentials:
        info = self.get_user_credentials_info(user=user)
        credentials = Credentials.from_authorized_user_info(info=info)

        if not credentials.valid:
            gar = google_auth_requests.Request()
            credentials.refresh(gar)

        if credentials.valid:
            return credentials

        raise ValueError

    def get_credentials_info(self, credentials: Credentials) -> str:
        info: str

        if credentials.client_id == self.client_id:
            info = credentials.to_json(strip=["client_id", "client_secret"])
        else:
            info = credentials.to_json()

        return info


def get_gauth() -> GoogleOAuth:
    settings = Settings()
    return GoogleOAuth(settings=settings)
