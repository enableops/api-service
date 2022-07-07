from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, user, customers
from app.models import urls

api_router = APIRouter()

api_router.include_router(
    router=auth.router, prefix=urls.Sections.auth, tags=["auth"]
)

api_router.include_router(
    router=user.router,
    prefix="/user",
    tags=["user"],
)

api_router.include_router(
    router=customers.router,
    prefix="/customers",
    tags=["customers"],
)
