from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app import protocols as protos
from app import dependencies as deps
from app.database import crud

from . import projects

router: APIRouter = APIRouter()


@router.get("/gcloud_projects")
def get_user_project_ids(
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    user=Depends(deps.get_current_user),
    user_api: protos.UserAPI = Depends(deps.get_user_api),
):
    user_projects = user_api.get_project_ids()

    if user_api.credentials != user.credentials:
        user.credentials = user_api.credentials
        background_tasks.add_task(crud.user.update_user, db=db, user=user)

    return user_projects


@router.get("/auth_status")
def user_status(user_api: protos.UserAPI = Depends(deps.get_user_api)):
    return True


@router.get("/profile")
def get_user_profile(
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    user=Depends(deps.get_current_user),
    user_api: protos.UserAPI = Depends(deps.get_user_api),
):
    user_profile = user_api.get_profile()

    if user_api.credentials != user.credentials:
        user.credentials = user_api.credentials
        background_tasks.add_task(crud.user.update_user, db=db, user=user)

    return user_profile


router.include_router(router=projects.router, prefix="/projects")
