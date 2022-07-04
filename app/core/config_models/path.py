from pydantic import BaseModel


class PathConfig(BaseModel):
    """Stores routing settings"""

    AUTH_MODULE: str
    AUTH_REDIRECT: str
    AUTH_TOKEN: str
