from typing import Callable

from fastapi import FastAPI

# https://github.com/tiangolo/fastapi/issues/1442#issuecomment-788633654


def update_schema_name(app: FastAPI, function: Callable, name: str) -> None:
    # https://github.com/tiangolo/fastapi/issues/1442#issuecomment-788633654
    """
    Updates the Pydantic schema name for a FastAPI function that takes
    in a fastapi.UploadFile = File(...) or bytes = File(...).

    This is a known issue that was reported on FastAPI#1442 in which
    the schema for file upload routes were auto-generated with no
    customization options. This renames the auto-generated schema to
    something more useful and clear.

    Args:
        app: The FastAPI application to modify.
        function: The function object to modify.
        name: The new name of the schema.
    """
    for route in app.routes:
        if route.endpoint is function:  # type: ignore
            route.body_field.type_.__name__ = name  # type: ignore
            break
