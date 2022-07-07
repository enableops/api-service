from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.database.project import Project
from app.models import project as model


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

    if db_project is None:
        return None

    project_data = jsonable_encoder(project)
    for field in project_data:
        setattr(db_project, field, project_data[field])

    flag_modified(db_project, "status")
    flag_modified(db_project, "state")

    db.commit()
    db.refresh(db_project)

    return db_project
