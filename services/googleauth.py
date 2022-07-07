from dataclasses import dataclass
import os
from typing import List, Optional, Tuple

from google.auth.transport import requests as google_auth_requests
from google.oauth2.id_token import verify_oauth2_token
from google_auth_oauthlib.flow import Flow

from pydantic import BaseModel, BaseSettings, HttpUrl, parse_obj_as, validator

default_auth_uri = parse_obj_as(
    HttpUrl, "https://accounts.google.com/o/oauth2/auth"
)
default_token_uri = parse_obj_as(
    HttpUrl, "https://accounts.google.com/o/oauth2/token"
)


class OAuthSettings(BaseModel):
    client_id: str
    client_secret: str
    auth_uri: HttpUrl = default_auth_uri
    token_uri: HttpUrl = default_token_uri
    access_type: str = "offline"
    prompt_type: str = "consent"
    scopes: List[str] = []

    @validator("scopes", pre=True)
    def assemble_scopes(cls, v: str) -> List[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v


class Settings(BaseSettings):
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
        self.client_id = settings.oauth.client_id
        self.client_secret = settings.oauth.client_secret
        self.auth_uri = settings.oauth.auth_uri
        self.token_uri = settings.oauth.token_uri
        self.scopes = settings.oauth.scopes
        self.access_type = settings.oauth.access_type
        self.prompt_type = settings.oauth.prompt_type

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

        return GoogleOAuthUser(
            uid=identity["sub"],
            email=identity["email"],
            credentials=credentials.to_json(),
        )


def get_gauth() -> GoogleOAuth:
    settings = Settings()
    return GoogleOAuth(settings=settings)
