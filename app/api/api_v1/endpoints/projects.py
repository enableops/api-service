from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.param_functions import Path
from sqlalchemy.orm import Session

from app.database.crud import project as crud
from app.models import project as model
from app.models import user
from app.models.exception import APIException

from app import dependencies as deps
from app import protocols as protos

router: APIRouter = APIRouter()


def check_project_access(user_api: protos.UserAPI, project_id: str):
    user_project_ids = [
        project.get("id") for project in user_api.get_project_ids()
    ]

    return project_id in user_project_ids


def update_project_state_history(
    *, project: model.Project, new_status: model.ProjectStatus
):
    if project.status == new_status:
        return project

    project.status = new_status
    project.state.history.append({new_status: model.ProjectStatusDetails()})

    return project


@router.get("/", response_model=List[model.ProjectResponse])
def get_user_projects(
    user: user.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    projects = crud.get_user_projects(
        db=db, owner_id=user.id, skip=skip, limit=limit
    )

    return projects


@router.get("/{project_id}", response_model=model.ProjectResponse)
def get_project(
    project_id: str = Path(..., description="project id"),
    user: user.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    project = crud.get_user_project(
        db=db, project_id=project_id, owner_id=user.id
    )

    if project:
        return project

    raise APIException.NOPROJECT404


@router.delete("/{project_id}")
def delete_project(
    background_tasks: BackgroundTasks,
    project_id: str = Path(..., description="project id"),
    user: user.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    db_project = crud.get_user_project(
        db=db, project_id=project_id, owner_id=user.id
    )

    if db_project:
        background_tasks.add_task(
            crud.update_project_status,
            db_project=db_project,
            db=db,
            new_status=model.ProjectStatus.REMOVE_REQUIRED,
        )

        return {"detail": "ok"}

    raise APIException.NOPROJECT404


@router.post("/", response_model=model.ProjectResponse)
def configure_project(
    project: model.ProjectCreate,
    background_tasks: BackgroundTasks,
    user: user.User = Depends(deps.get_current_user),
    user_api: protos.UserAPI = Depends(deps.get_user_api),
    db: Session = Depends(deps.get_db),
    infrastructure: protos.Infrastructure = Depends(deps.get_infrastructure),
):
    if (
        check_project_access(user_api=user_api, project_id=project.project_id)
        is False
    ):
        raise APIException.NOTYOURS403

    db_project = crud.get_user_project(
        db=db, project_id=project.project_id, owner_id=user.id
    )

    # create if not found
    if not db_project:
        db_project = crud.create_project(
            db=db, project=project, user_id=user.id
        )

    user_project = model.Project.from_orm(db_project)

    user_project = update_project_state_history(
        project=user_project, new_status=model.ProjectStatus.CONFIGURE_REQUIRED
    )

    if infrastructure.request_update():
        user_project = update_project_state_history(
            project=user_project,
            new_status=model.ProjectStatus.CONFIGURE_DISPATCHED,
        )
    else:
        user_project = update_project_state_history(
            project=user_project,
            new_status=model.ProjectStatus.CONFIGURE_FAILED,
        )

    background_tasks.add_task(
        crud.update_project,
        db=db,
        project=user_project,
    )

    return user_project
