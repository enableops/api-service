from __future__ import annotations

from datetime import datetime
from enum import Enum, auto
from typing import Dict, List

from pydantic import BaseModel, Field

from app.models.user import UserInfo

current_timestamp = lambda: int(datetime.timestamp(datetime.now()))

class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class ProjectStatus(str, AutoName):
    CREATED = auto()

    CONFIGURE_REQUIRED = auto()
    CONFIGURE_DISPATCHED = auto()
    CONFIGURE_FAILED = auto()
    CONFIGURED = auto()

    REMOVE_REQUIRED = auto()
    REMOVE_DISPATCHED = auto()
    REMOVE_FAILED = auto()
    REMOVED = auto()

    @classmethod
    def list_active(cls) -> List[ProjectStatus]:
        return [
            ProjectStatus.CONFIGURE_REQUIRED,
            ProjectStatus.CONFIGURE_DISPATCHED,
            ProjectStatus.CONFIGURE_FAILED,
            ProjectStatus.CONFIGURED,
        ]


class ProjectStatusDetails(BaseModel):
    time: int = Field(default_factory=current_timestamp)
    variables: Dict[str, str] = {}


class ProjectState(BaseModel):
    version: str = "v1"
    history: List[Dict[ProjectStatus, ProjectStatusDetails]] = Field(
        default_factory=list
    )


class ProjectBase(BaseModel):
    project_id: str = Field(
        ...,
        description="Id of project in Google Cloud Computing Services",
        example="google_cloud_project_id",
    )
    flavour: str = Field(
        ...,
        description="Initial configuration on initialization",
        example="python",
    )


class ProjectCreate(ProjectBase):
    pass


class ProjectConfiguration(ProjectBase):
    owner: UserInfo

    class Config:
        orm_mode = True


class ProjectResponse(ProjectBase):
    created_at: int = Field(
        default_factory=current_timestamp,
        description="Date and time of project deploy",
        example=int(datetime.timestamp(datetime.now())),
    )

    status: ProjectStatus = Field(
        ProjectStatus.CREATED,
        description="Status of project deployment",
        example=ProjectStatus.CREATED,
    )

    state: ProjectState = Field(
        ..., description="Object describing current state"
    )

    class Config:
        orm_mode = True


class Project(ProjectResponse):
    owner_id: int
