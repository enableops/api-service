"""Base class for all db models.

Contains fixed naming convention for propper migrations,
and attributes for table name and created_at for every item in db.
"""

from sqlalchemy import Column, Integer, MetaData
from sqlalchemy.ext.declarative import as_declarative, declared_attr

from app.services.helpers import current_timestamp

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)


@as_declarative(metadata=metadata)
class CustomBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @declared_attr
    def created_at(cls):
        return Column(
            Integer(),
            default=current_timestamp,
            nullable=False,
        )
