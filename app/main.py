"""Prepare app instance.

- Initialize app instance
- Add secure sessions middleware
- Setup and add CORS filtering
- Initialize DB session
"""
import secrets

import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app import settings
from app.api.api_v1.api import api_router

# App
# Instantiate app
app_settings = settings.Settings().api
app_name = app_settings.name
app_description = app_settings.description
app_version = app_settings.version

app = FastAPI(
    title=app_name,
    description=app_description,
    version=app_version,
    openapi_url="/v1/openapi.json",
)

# Setup logging
sentry_dsn = app_settings.sentry_dsn
if sentry_dsn:
    if "dev" in app_version or app_version == "0.0.0":
        environment = "debug"
    else:
        environment = "prod"

    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        release=app_version,
    )
    app.add_middleware(SentryAsgiMiddleware)

# Add CORS Security
if app_settings.cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in app_settings.cors],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

# Create ability to save data on enduser side
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_hex(32),
    same_site="strict",
    https_only=True,
)


# Database & session init
engine = create_engine(
    app_settings.db_url, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Add main api router
app.include_router(api_router, prefix="/v1")
