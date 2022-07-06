from typing import List

from pydantic import AnyHttpUrl, BaseModel, validator


class SecurityConfig(BaseModel):
    """Stores settings for security related elements"""

    TERRAFORM_SECRET: str

    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SESSION_SIGN_KEY: str
    DB_CRYPTO_KEY: bytes

    @validator("DB_CRYPTO_KEY", pre=True)
    def convert_crypto_key(cls, v: str):
        return bytes.fromhex(v)

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str) -> List[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v
