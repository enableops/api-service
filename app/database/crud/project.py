from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.database.project import Project
from app.models import project as model

# from app.services.github import dispatch_apply_workflow


def get_project(db: Session, project_id: str) -> Optional[Project]:
    return db.query(Project).filter(Project.project_id == project_id).first()


def get_all_projects(db: Session) -> Optional[Project]:
    return db.query(Project)


def get_user_project(db: Session, project_id: str, owner_id: int):
    return (
        db.query(Project)
        .filter(Project.project_id == project_id, Project.owner_id == owner_id)
        .first()
    )


def get_user_projects(
    db: Session,
    owner_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
):
    if not owner_id is None:
        query = db.query(Project).filter(Project.owner_id == owner_id)
    else:
        query = db.query(Project)

    return query.offset(skip).limit(limit).all()


def get_all_active_projects(
    db: Session,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(Project).filter(
        Project.status.in_(model.ProjectStatus.list_active())
    )

    return query.offset(skip).limit(limit).all()


def create_project(
    db: Session, project: model.ProjectCreate, user_id: int
) -> Project:
    state = model.ProjectState(
        history=[{model.ProjectStatus.CREATED: model.ProjectStatusDetails()}]
    )

    new_project = model.Project(
        project_id=project.project_id,
        flavour=project.flavour,
        owner_id=user_id,
        state=state,
    )

    db_project = Project(**jsonable_encoder(new_project))
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_project(db: Session, project: model.Project) -> Optional[Project]:
    db_project = get_project(db=db, project_id=project.project_id)

    if db_project:
        db_project.status = project.status
        db_project.state["history"] = jsonable_encoder(project.state.history)

        flag_modified(db_project, "status")
        flag_modified(db_project, "state")

        db.commit()
        db.refresh(db_project)

        return db_project

    return None


def update_project_status(
    db_project: Project, db: Session, new_status: model.ProjectStatus
) -> Optional[Project]:
    project = model.Project.from_orm(db_project)

    if project.status == new_status:
        return db_project

    is_currently_active = project.status in model.ProjectStatus.list_active()
    will_be_active = new_status in model.ProjectStatus.list_active()

    project.status = new_status

    if is_currently_active != will_be_active:  # if we're switching on/off
        # FIXME: come up with better structure for status
        if new_status == model.ProjectStatus.REMOVE_REQUIRED:
            failed = model.ProjectStatus.REMOVE_FAILED
        else:
            failed = model.ProjectStatus.CONFIGURE_FAILED

        # if not dispatch_apply_workflow():
        #     new_status = failed

    project.status = new_status
    project.state.history.append({project.status: model.ProjectStatusDetails()})

    return update_project(db=db, project=project)
