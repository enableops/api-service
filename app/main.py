"""Prepare app instance.

- Initialize app instance
- Add secure sessions middleware
- Setup and add CORS filtering
- Initialize DB session
"""

import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from app.core.config import settings

from services import github

from app.api.api_v1.api import api_router

# App
# Instantiate app
app_name = settings.PROJECT_NAME
app_version = settings.VERSION

app = FastAPI(
    title=app_name,
    version=app_version,
    openapi_url="/v1/openapi.json",
)

# Setup logging
sentry_dsn = settings.SENTRY_DSN
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
CORS_SETTINGS = settings.SECURITY.BACKEND_CORS_ORIGINS
if CORS_SETTINGS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in CORS_SETTINGS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

# Create ability to save data on enduser side
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECURITY.SESSION_SIGN_KEY,
    same_site="strict",
    https_only=True,
)


# Database & session init
engine = create_engine(
    settings.DB.URI, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Add main api router
app.include_router(api_router, prefix="/v1")


# Fix naming form some schemas
# TODO: Clean it up somehow - find a way to set Schema naming
update_schema_name(app=app, function=get_token, name="AuthTokenForm")
