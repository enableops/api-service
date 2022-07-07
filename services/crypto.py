import logging
import os
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import BaseSettings


default_key = b"pls help me god!"


class Settings(BaseSettings):
    key: bytes = default_key

    class Config:
        env_prefix = "CRYPTO_"
        secrets_dir = os.getenv("SECRETS_PATH")


class Crypto:
    key: bytes

    def __init__(self, *, settings: Settings):
        self.key = settings.key

    def encrypt(self, *, string: str) -> bytes:
        nonce = secrets.token_bytes(12)
        payload = string.encode()
        token = nonce + AESGCM(self.key).encrypt(nonce, payload, b"")
        return token

    def decrypt(self, *, token: bytes) -> str:
        payload = AESGCM(self.key).decrypt(token[:12], token[12:], b"")
        return payload.decode()


def get_crypto():
    settings = Settings()

    if settings.key == default_key:
        logger = logging.getLogger("uvicorn")
        logger.critical("Using default data encryption key")

    return Crypto(settings=settings)
