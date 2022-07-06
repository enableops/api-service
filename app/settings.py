import os
from typing import List, Optional

from pydantic import BaseModel, AnyHttpUrl
import tomli


with open("pyproject.toml", "rb") as f:
    project_info = tomli.load(f)["tool"]["poetry"]

default_session_key = "dev"


class APISettings(BaseModel):
    NAME: str = project_info["name"]
    DESCRIPTION: str = project_info["description"]
    VERSION: str = project_info["version"]
    SENTRY_DSN: Optional[str] = None
    CORS: List[AnyHttpUrl] = []
    SESSION_KEY: str = default_session_key
    DB_URL: str = "sqlite:///database.sqlite"


class Settings(BaseModel):
    api: APISettings

    class Config:
        env_nested_delimiter = "__"
        secrets_dir = os.getenv("SECRETS_PATH")
