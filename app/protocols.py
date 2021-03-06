from typing import Dict, List, Optional, Protocol, Tuple


class Infrastructure(Protocol):
    def request_update(self) -> bool:
        ...


class Encryption(Protocol):
    def encrypt(self, string: str) -> bytes:
        ...

    def decrypt(self, token: bytes) -> str:
        ...


class OAuthUser(Protocol):
    uid: str
    email: str
    credentials: str


class OAuth(Protocol):
    client_id: str
    prompt_type: str
    access_type: str
    scopes: str

    def get_auth_url_with_state(
        self, *, redirect_uri: str, state: Optional[str]
    ) -> Tuple[str, str]:
        ...

    def get_user_from_authcode(
        self, *, code: str, redirect_uri: str, state: str
    ) -> OAuthUser:
        ...


class Token(Protocol):
    access_token: str
    csrf_token: str
    token_type: str


class TokenService(Protocol):
    def create_access_token(self, *, for_sub: str) -> Token:
        ...


class UserAPI(Protocol):
    credentials: str

    def __init__(self, *, credentials: str):
        ...

    def get_project_ids(self) -> List[Dict[str, str]]:
        ...

    def get_profile(self) -> Dict[str, str]:
        ...
