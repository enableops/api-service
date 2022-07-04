import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import BaseModel

from app.core.config import settings


class Crypto(BaseModel):
    key: bytes = settings.SECURITY.DB_CRYPTO_KEY

    def encrypt(self, string: str) -> bytes:
        nonce = secrets.token_bytes(12)
        payload = string.encode()
        token = nonce + AESGCM(self.key).encrypt(nonce, payload, b"")
        return token

    def decrypt(self, token: bytes) -> str:
        payload = AESGCM(self.key).decrypt(token[:12], token[12:], b"")
        return payload.decode()


crpt = Crypto()
