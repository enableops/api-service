from typing import Optional, Protocol, Tuple


class Infrastructure(Protocol):
    def infrastructure_update(self) -> bool:
        ...


class Encryption(Protocol):
    def encrypt(self, string: str) -> bytes:
        ...

    def decrypt(self, token: bytes) -> str:
        ...


class OAuth(Protocol):
    def get_auth_url_with_state(
        self, *, redirect_uri: str, state: Optional[str]
    ) -> Tuple[str, str]:
        ...

    def get_user_from_authcode(
        self, *, code: str, redirect_url: str, state: str
    ):
        ...


class OAuthUser(Protocol):
    uid: str
    email: str
    credentials: str
