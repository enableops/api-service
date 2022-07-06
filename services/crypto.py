import logging
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import BaseModel


default_key = b"pls help me god!"


class Settings(BaseModel):
    key: bytes = default_key

    class Config:
        env_prefix = "CRYPTO_"


class Crypto:
    key: bytes

    def __init__(self, *, settings: Settings):
        if self.key == default_key:
            logging.exception("Using default key for data encryption")

        self.key = settings.key

    def encrypt(self, string: str) -> bytes:
        nonce = secrets.token_bytes(12)
        payload = string.encode()
        token = nonce + AESGCM(self.key).encrypt(nonce, payload, b"")
        return token

    def decrypt(self, token: bytes) -> str:
        payload = AESGCM(self.key).decrypt(token[:12], token[12:], b"")
        return payload.decode()
