"""Database schema for project."""
from sqlalchemy import (
    JSON,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database.custom_base import CustomBase
from app.database.user import User


class Project(CustomBase):
    """DB model for project of the enableops."""

    __table_args__ = (UniqueConstraint("project_id", "owner_id"),)

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, unique=True, index=True, nullable=False)
    flavour = Column(String, index=True, nullable=False)
    status = Column(String, index=True, nullable=False)
    state = Column(JSON)

    owner_id = Column(Integer, ForeignKey(f"{User.__tablename__}.id"))
    owner = relationship("User", back_populates="projects")
