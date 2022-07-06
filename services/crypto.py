import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import BaseModel, Field

from app.core.config import settings

generate_random_key = lambda: secrets.token_bytes(32)


class Settings(BaseModel):
    key: bytes = Field(default_factory=generate_random_key)

    class Config:
        env_prefix = "CRYPTO_"


class Crypto:
    key: bytes

    def __init__(self, *, settings: Settings):
        self.key = settings.key

    def encrypt(self, string: str) -> bytes:
        nonce = secrets.token_bytes(12)
        payload = string.encode()
        token = nonce + AESGCM(self.key).encrypt(nonce, payload, b"")
        return token

    def decrypt(self, token: bytes) -> str:
        payload = AESGCM(self.key).decrypt(token[:12], token[12:], b"")
        return payload.decode()
