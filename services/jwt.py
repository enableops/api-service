from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import os
import secrets
from typing import Any

from jose import jwt
from pydantic import BaseModel

default_encryption_key = "hello world!"


class JWTSettings(BaseModel):
    token_expire_minutes: int
    encryption_key: str = default_encryption_key

    repo: str
    workflow_file: str
    ref: str


class Settings(BaseModel):
    jwt: JWTSettings

    class Config:
        env_nested_delimiter = "__"
        secrets_dir = os.getenv("SECRETS_PATH")


@dataclass
class Token:
    access_token: str
    csrf_token: str
    token_type: str


class JWT:
    token_expire_minutes: int
    encryption_key: str
    algorithm: str

    def __init__(
        self,
        *,
        token_expire_minutes: int,
        encryption_key: str,
        algorithm: str = "HS256",
    ):
        self.token_expire_minutes = token_expire_minutes
        self.encryption_key = encryption_key
        self.algorithm = algorithm

    def create_access_token(self, *, for_sub: str) -> Token:
        ttl = timedelta(minutes=self.token_expire_minutes)
        csrf_secret = secrets.token_hex(32)

        data = {"sub": for_sub, "csrf_secret": csrf_secret}
        access_token = self.generate_token(data=data, expires_delta=ttl)

        csrf_token = self.generate_token(
            data={"csrf_secret": csrf_secret},
            expires_delta=ttl,
        )

        return Token(
            access_token=access_token,
            csrf_token=csrf_token,
            token_type="bearer",
        )

    def generate_token(self, *, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()

        expire_datetime = datetime.now() + expires_delta
        exp_timestamp = int(datetime.timestamp(expire_datetime))

        to_encode.update({"exp": exp_timestamp})

        encoded_jwt = jwt.encode(
            to_encode,
            self.encryption_key,
            algorithm=self.algorithm,
        )

        if type(encoded_jwt) is str:
            return encoded_jwt
        else:
            raise ValueError

    def decode(self, *, jwt_token: str) -> dict:
        payload = jwt.decode(
            jwt_token,
            self.encryption_key,
            algorithms=self.algorithm,
        )

        if type(payload) is dict:
            return payload
        else:
            raise ValueError


def get_jwt() -> JWT:
    settings = Settings().jwt

    if settings.encryption_key == default_encryption_key:
        logging.exception("Using default JWT encryption key")

    return JWT(
        token_expire_minutes=settings.token_expire_minutes,
        encryption_key=settings.encryption_key,
    )
