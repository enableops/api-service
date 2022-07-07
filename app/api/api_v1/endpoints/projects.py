from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.param_functions import Path
from sqlalchemy.orm import Session

# from app.api.dependencies import get_db, get_user_gapi
from app.database.crud import project as crud
from app.models import project as model
from app.models.exception import APIException

# from app.services.github import dispatch_apply_workflow
# from app.services.google_api import GoogleUserAPI

router: APIRouter = APIRouter()


# @router.get("/", response_model=List[model.ProjectResponse])
# def get_user_projects(
#     user_api: GoogleUserAPI = Depends(get_user_gapi),
#     db: Session = Depends(get_db),
#     skip: int = 0,
#     limit: int = 100,
# ):
#     projects = crud.get_user_projects(
#         db=db, owner_id=user_api.user.id, skip=skip, limit=limit
#     )

#     return projects


# @router.get("/{project_id}", response_model=model.ProjectResponse)
# def get_project(
#     project_id: str = Path(..., description="project id"),
#     user_api: GoogleUserAPI = Depends(get_user_gapi),
#     db: Session = Depends(get_db),
# ):
#     project = crud.get_user_project(
#         db=db, project_id=project_id, owner_id=user_api.user.id
#     )

#     if project:
#         return project

#     raise APIException.NOPROJECT404


# @router.delete("/{project_id}")
# def delete_project(
#     background_tasks: BackgroundTasks,
#     project_id: str = Path(..., description="project id"),
#     user_api: GoogleUserAPI = Depends(get_user_gapi),
#     db: Session = Depends(get_db),
# ):
#     db_project = crud.get_user_project(
#         db=db, project_id=project_id, owner_id=user_api.user.id
#     )

#     if db_project:
#         background_tasks.add_task(
#             crud.update_project_status,
#             db_project=db_project,
#             db=db,
#             new_status=model.ProjectStatus.REMOVE_REQUIRED,
#         )

#         return {"detail": "ok"}

#     raise APIException.NOPROJECT404


# @router.post("/", response_model=model.ProjectResponse)
# def configure_project(
#     project: model.ProjectCreate,
#     background_tasks: BackgroundTasks,
#     user_api: GoogleUserAPI = Depends(get_user_gapi),
#     db: Session = Depends(get_db),
# ):
#     user_project_ids = [
#         project.get("id") for project in user_api.get_project_ids()
#     ]

#     if project.project_id not in user_project_ids:
#         raise APIException.NOTYOURS403

#     db_project = crud.get_user_project(
#         db=db, project_id=project.project_id, owner_id=user_api.user.id
#     )

#     # create if not found
#     if not db_project:
#         db_project = crud.create_project(
#             db=db, project=project, user_id=user_api.user.id
#         )

#     background_tasks.add_task(
#         crud.update_project_status,
#         db_project=db_project,
#         db=db,
#         new_status=model.ProjectStatus.CONFIGURE_REQUIRED,
#     )

#     return db_project
