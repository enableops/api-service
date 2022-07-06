from typing import Set
from pydantic import BaseModel


class IncomingCustomersUpdate(BaseModel):
    before: Set[str]
    after: Set[str]
