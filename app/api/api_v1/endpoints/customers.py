from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

from app.database.crud import project as crud
from app.models import project
from app.models import terraform

from app import dependencies as deps
from app import settings

from .projects import update_project_state_history

router: APIRouter = APIRouter()


@router.get("/projects", response_model=List[project.ProjectConfiguration])
def get_active_projects(
    db: Session = Depends(deps.get_db),
    terraform_token: str = Header(..., description="Auth header"),
):
    no_auth_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )

    config = settings.Settings().api
    if terraform_token != config.terraform_key:
        raise no_auth_exception

    return crud.get_all_active_projects(db=db)


@router.post("/apply")
def post_apply_status(
    terraform_update: terraform.IncomingCustomersUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    terraform_token: str = Header(..., description="Auth header"),
):
    no_auth_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )

    config = settings.Settings().api
    if terraform_token != config.terraform_key:
        raise no_auth_exception

    added = terraform_update.after

    for db_project in crud.get_all_projects(db=db):
        if db_project.project_id in added:
            new_status = project.ProjectStatus.CONFIGURED
            blocking_requirements = [
                project.ProjectStatus.REMOVE_REQUIRED.value,
                project.ProjectStatus.REMOVE_FAILED.value,
            ]
        else:
            new_status = project.ProjectStatus.REMOVED
            blocking_requirements = [
                project.ProjectStatus.CONFIGURE_REQUIRED.value,
                project.ProjectStatus.CONFIGURE_FAILED.value,
            ]

        if db_project.status not in blocking_requirements:
            user_project = project.Project.from_orm(db_project)
            user_project = update_project_state_history(
                project=user_project, new_status=new_status
            )

            background_tasks.add_task(
                crud.update_project,
                db=db,
                project=user_project,
            )

    return {"detail": "ok"}
