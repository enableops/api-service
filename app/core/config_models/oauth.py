from typing import Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, validator


class OAuthConfig(BaseModel):
    """Stores all values for operating OAuth login"""

    CLIENT_ID: str
    CLIENT_SECRET: str
    AUTH_URI: str
    TOKEN_URI: str
    ACCESS_TYPE: str
    PROMPT_TYPE: str
    SCOPES: List[str]

    @validator("SCOPES", pre=True)
    def assemble_scopes(cls, v: str) -> List[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    REDIRECT_HOST: AnyHttpUrl

    SWAGGER_REDIRECT_PATH: str
