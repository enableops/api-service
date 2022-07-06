"""Database schema for User."""
from sqlalchemy import Column, Integer, LargeBinary, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.database.custom_base import CustomBase

from services import crypto


class User(CustomBase):
    """DB model for user of the API."""

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    token = Column(LargeBinary, nullable=False)

    @hybrid_property
    def credentials(self) -> str:
        crpt = crypto.get_crypto()
        return crpt.decrypt(token=self.token)

    @credentials.setter  # type: ignore
    def credentials(self, value: str) -> None:
        crpt = crypto.get_crypto()
        self.token = crpt.encrypt(string=value)

    def __init__(self, uid: str, email: str, credentials: str) -> None:
        crpt = crypto.get_crypto()
        self.uid = uid
        self.email = email
        self.token = crpt.encrypt(string=credentials)

    projects = relationship("Project", back_populates="owner")
