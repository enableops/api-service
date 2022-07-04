import os
from typing import Optional, Dict, Any
from pathlib import Path
from copy import deepcopy

import tomli
from pydantic import BaseSettings

from app.core.config_models.db import DatabaseConfig
from app.core.config_models.github import GithubConfig
from app.core.config_models.oauth import OAuthConfig
from app.core.config_models.path import PathConfig
from app.core.config_models.security import SecurityConfig


def get_version_from_toml(file_path: str):
    with open(file_path, "rb") as f:
        toml_dict = tomli.load(f)
        return toml_dict["tool"]["poetry"]["version"]


# TODO: hide this into helpers class
def deep_dicts_merge(d1, d2):
    result = {}
    overlapping_keys = d1.keys() & d2.keys()
    for key in overlapping_keys:
        result[key] = deep_dicts_merge(d1[key], d2[key])
    for key in d1.keys() - overlapping_keys:
        result[key] = deepcopy(d1[key])
    for key in d2.keys() - overlapping_keys:
        result[key] = deepcopy(d2[key])
    return result


def path_list_to_dict(path_list):
    if len(path_list) == 1:
        return path_list[0]
    elif len(path_list):
        return {path_list[0]: path_list_to_dict(path_list[1:])}
    return path_list


# TODO: allow have extra fields and not to crash
def nested_file_secrets_settings(settings: BaseSettings) -> Dict[str, Any]:
    secrets_dir = settings.__config__.secrets_dir

    if secrets_dir is None:
        return {}

    delimiter = settings.__config__.env_nested_delimiter
    env_prefix = settings.__config__.env_prefix

    if secrets_dir is None or delimiter is None:
        return {}
    dir = Path(secrets_dir)
    secrets = []

    for file in dir.glob("*"):
        content = file.read_text(encoding="utf-8").strip()
        name = file.name.removeprefix(env_prefix)
        secrets.append(name.split(delimiter) + [content])

    result = {}
    for secret in secrets:
        result = deep_dicts_merge(result, path_list_to_dict(secret))

    return result


class APIConfig(BaseSettings):
    """API configurations."""

    PROJECT_NAME: str
    ENV_STATE: str
    VERSION: str = get_version_from_toml("pyproject.toml")

    SENTRY_DSN: str

    PATH: PathConfig
    SECURITY: SecurityConfig
    OAUTH: OAuthConfig
    GITHUB: GithubConfig
    DB: DatabaseConfig

    class Config:
        case_sensitive = True
        env_nested_delimiter = "__"
        env_prefix: str = "API_"
        secrets_dir = os.getenv("API_SECRETS_PATH")

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                env_settings,
                nested_file_secrets_settings,
            )


settings = APIConfig()
