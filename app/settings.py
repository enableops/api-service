import os
from typing import List, Optional

from pydantic import BaseModel, AnyHttpUrl, BaseSettings, parse_obj_as
import tomli


with open("pyproject.toml", "rb") as f:
    project_info = tomli.load(f)["tool"]["poetry"]

default_session_key = "dev"
default_host_url = parse_obj_as(AnyHttpUrl, "http://127.0.0.1:8000")
default_db_url = "sqlite:///database.sqlite"
default_terraform_key = "terraform"


class APISettings(BaseModel):
    name: str = project_info["name"]
    description: str = project_info["description"]
    version: str = project_info["version"]
    sentry_dsn: Optional[str] = None
    cors: List[AnyHttpUrl] = []
    session_key: str = default_session_key
    db_url: str = default_db_url
    host_url: AnyHttpUrl = default_host_url
    terraform_key: str = default_terraform_key


class Settings(BaseSettings):
    api: APISettings = parse_obj_as(APISettings, {})

    class Config:
        env_nested_delimiter = "__"
        secrets_dir = os.getenv("SECRETS_PATH")
