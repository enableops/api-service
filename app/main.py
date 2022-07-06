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


# App
# Instantiate app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/v1/openapi.json",
)

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


# Create ability to report errors to Sentry
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENV_STATE,
    release=settings.VERSION,
)
app.add_middleware(SentryAsgiMiddleware)


# Database & session init
engine = create_engine(
    settings.DB.URI, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Link infrastructure
github_config = github.Settings()
github = github.Github(settings=github_config)


# Routes
# TODO: Fix circular dependency
from app.api.api_v1.api import api_router  # noqa: E402
from app.api.api_v1.endpoints.auth import get_token  # noqa: E402
from app.services.openapi import update_schema_name  # noqa: E402


# Add redirect to docs
@app.get("/", include_in_schema=False)
def redirect_to_docs() -> RedirectResponse:
    """Redirects to /docs.

    Redirect from empty root endpoint to /docs endpoint,
    which provides a convinient way to go for docs.
    """
    return RedirectResponse("/docs")


# Add main api router
app.include_router(api_router, prefix="/v1")


# Fix naming form some schemas
# TODO: Clean it up somehow - find a way to set Schema naming
update_schema_name(app=app, function=get_token, name="AuthTokenForm")
