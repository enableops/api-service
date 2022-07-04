from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, user, customers
from app.core.config import settings

api_router = APIRouter()

api_router.include_router(
    router=auth.router, prefix=settings.PATH.AUTH_MODULE, tags=["auth"]
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
