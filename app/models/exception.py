from enum import Enum
from typing import NamedTuple

from fastapi import HTTPException

ExceptionSettings = NamedTuple(
    "ExceptionSettings", [("status_code", int), ("detail", str)]
)


class APIException(HTTPException, Enum):
    NOTYOURS403 = ExceptionSettings(
        status_code=403,
        detail=(
            "Sorry, you are not allowed to configure "
            "projects you don't have access to."
        ),
    )

    NOTYOU403 = ExceptionSettings(
        status_code=403,
        detail=(
            "Sorry, you are not allowed to access " "users that are not you."
        ),
    )

    NOPROJECT404 = ExceptionSettings(
        status_code=404, detail=("Project not found")
    )
