from fastapi import APIRouter, Depends

from app.api.dependencies import get_user_gapi
from app.services.google_api import GoogleUserAPI

from . import projects

router: APIRouter = APIRouter()


@router.get("/gcloud_projects")
def get_user_project_ids(user_api: GoogleUserAPI = Depends(get_user_gapi)):
    return user_api.get_project_ids()


@router.get("/auth_status")
def user_status(user_api: GoogleUserAPI = Depends(get_user_gapi)):
    return True


@router.get("/profile")
def get_user_profile(user_api: GoogleUserAPI = Depends(get_user_gapi)):
    return user_api.get_profile()


router.include_router(router=projects.router, prefix="/projects")
