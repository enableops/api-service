import re
from typing import Dict, Optional

import requests
from pydantic import BaseModel, PostgresDsn, validator


def get_heroku_db_uri(app_name: str, token: str) -> Optional[str]:
    url = f"https://api.heroku.com/apps/{app_name}/config-vars"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.heroku+json; version=3",
    }

    config_vars: dict[str, str] = requests.get(url, headers=headers).json()
    database_url = config_vars.get("DATABASE_URL")
    return database_url


def fix_postgres_protocol(uri: str) -> str:
    return re.sub(r"^(postgres://)", "postgresql://", uri)


class DatabaseConfig(BaseModel):
    """Stores db settings"""

    USER: Optional[str] = None
    PASSWORD: Optional[str] = None
    SERVER: Optional[str] = None
    DB: Optional[str] = None

    HEROKU_APP_ID_OR_NAME: Optional[str] = None
    HEROKU_API_KEY: Optional[str] = None

    URI: Optional[str] = None

    @validator("URI", pre=True, always=True)
    def assemble_db_connection(
        cls, v: Optional[str], values: Dict[str, str]
    ) -> str:
        if isinstance(v, str):
            return fix_postgres_protocol(v)

        user = values.get("USER")
        password = values.get("PASSWORD")
        host = values.get("SERVER")
        db = values.get("DB")

        if None not in (user, password, host, db):
            return PostgresDsn.build(
                scheme="postgresql",
                user=user,
                password=password,
                host=host,
                path=f"/{db or ''}",
            )

        heroku_app = str(values.get("HEROKU_APP_ID_OR_NAME"))
        heroku_token = str(values.get("HEROKU_API_KEY"))

        if None not in (heroku_app, heroku_token):
            database_url = get_heroku_db_uri(
                app_name=heroku_app, token=heroku_token
            )

            if database_url:
                return fix_postgres_protocol(database_url)

        raise ValueError(v)
