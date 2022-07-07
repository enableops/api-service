from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

# from app.core.config import settings
# from app.api.dependencies import get_db
from app.database.crud import project as crud
from app.models import project
from app.models import terraform

router: APIRouter = APIRouter()


# @router.get("/projects", response_model=List[project.ProjectConfiguration])
# def get_active_projects(
#     db: Session = Depends(get_db),
#     terraform_token: str = Header(..., description="Auth header"),
# ):
#     no_auth_exception = HTTPException(
#         status_code=HTTP_401_UNAUTHORIZED,
#         detail="Not authenticated",
#     )

#     if terraform_token != settings.SECURITY.TERRAFORM_SECRET:
#         raise no_auth_exception

#     return crud.get_all_active_projects(db=db)


# @router.post("/apply")
# def post_apply_status(
#     terraform_update: terraform.IncomingCustomersUpdate,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db),
#     terraform_token: str = Header(..., description="Auth header"),
# ):
#     no_auth_exception = HTTPException(
#         status_code=HTTP_401_UNAUTHORIZED,
#         detail="Not authenticated",
#     )

#     if terraform_token != settings.SECURITY.TERRAFORM_SECRET:
#         raise no_auth_exception

#     added = terraform_update.after

#     for db_project in crud.get_all_projects(db=db):
#         if db_project.project_id in added:
#             new_status = project.ProjectStatus.CONFIGURED
#             blocking_requirements = [
#                 project.ProjectStatus.REMOVE_REQUIRED.value,
#                 project.ProjectStatus.REMOVE_FAILED.value,
#             ]
#         else:
#             new_status = project.ProjectStatus.REMOVED
#             blocking_requirements = [
#                 project.ProjectStatus.CONFIGURE_REQUIRED.value,
#                 project.ProjectStatus.CONFIGURE_FAILED.value,
#             ]

#         if db_project.status not in blocking_requirements:
#             background_tasks.add_task(
#                 crud.update_project_status,
#                 db_project=db_project,
#                 db=db,
#                 new_status=new_status,
#             )

#     return {"detail": "ok"}
