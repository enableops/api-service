import secrets
from typing import Optional

from fastapi import Form
from pydantic import BaseModel


class TokenRequest(BaseModel):
    code: str
    client_id: Optional[str]
    client_secret: Optional[str]
    redirect_uri: str


class TokenRequestForm(TokenRequest):
    def __init__(
        self,
        code: str = Form(...),
        redirect_uri: str = Form(...),
        client_id: Optional[str] = Form(None),
        client_secret: Optional[str] = Form(None),
    ):
        super().__init__(
            code=code,
            redirect_uri=redirect_uri,
            client_id=client_id,
            client_secret=client_secret,
        )


class Token(BaseModel):
    access_token: str
    csrf_token: str
    token_type: str


class TokenData(BaseModel):
    sub: str
    csrf_secret: str = secrets.token_hex(32)
