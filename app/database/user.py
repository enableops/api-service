"""Database schema for User."""
from sqlalchemy import Column, Integer, LargeBinary, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.database.custom_base import CustomBase
from app.services.cryptography import crpt


class User(CustomBase):
    """DB model for user of the API."""

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    token = Column(LargeBinary, nullable=False)

    @hybrid_property
    def credentials(self) -> str:
        return crpt.decrypt(token=self.token)

    @credentials.setter  # type: ignore
    def credentials(self, value: str) -> None:
        self.token = crpt.encrypt(string=value)

    # TODO: Find a propper way to define hybrid_property without custom init
    def __init__(self, uid: str, email: str, credentials: str) -> None:
        self.uid = uid
        self.email = email
        self.token = crpt.encrypt(string=credentials)

    projects = relationship("Project", back_populates="owner")
