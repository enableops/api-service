from typing import Set
from pydantic import BaseModel


class TerraformUpdate(BaseModel):
    before: Set[str]
    after: Set[str]
