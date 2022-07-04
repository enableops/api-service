from typing import Optional

from sqlalchemy.orm import Session

from app.database.user import User
from app.models import user as model


def get_user(db: Session, uid: str) -> Optional[User]:
    """Fetch a user from db, may return None."""
    return db.query(User).filter(User.uid == uid).first()


def create_user(db: Session, user: model.UserCreate) -> User:
    """Create new user and commit it to db."""
    db_user = User(
        uid=user.uid, email=user.email, credentials=user.credentials
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user: model.User) -> None:
    """Update user item with new data in db."""
    uid = user.uid
    credentials = user.credentials

    db_user = get_user(db=db, uid=uid)

    if db_user:
        db_user.credentials = credentials  # type: ignore

        db.commit()
        db.refresh(db_user)
    else:
        user = create_user(db=db, user=user)
