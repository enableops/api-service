from fastapi import APIRouter, Depends

from app import protocols as protos
from app import dependencies as deps

# from . import projects

router: APIRouter = APIRouter()


@router.get("/gcloud_projects")
def get_user_project_ids(user_api: protos.UserAPI = Depends(deps.get_user_api)):
    return user_api.get_project_ids()


@router.get("/auth_status")
def user_status(user_api: protos.UserAPI = Depends(deps.get_user_api)):
    return True


@router.get("/profile")
def get_user_profile(user_api: protos.UserAPI = Depends(deps.get_user_api)):
    return user_api.get_profile()


# router.include_router(router=projects.router, prefix="/projects")
