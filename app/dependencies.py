from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import settings
from app import main
from app import oauth
from services import googleauth, jwt, googleapi, github

from app.database.crud import user as crud
from app.models.token import TokenData
from app.models.user import User


async def get_db():
    db = main.SessionLocal()
    try:
        yield db
    finally:
        db.close()


get_oauth = lambda: googleauth.get_gauth()
get_token_service = lambda: jwt.get_jwt()
get_app_settings = lambda: settings.Settings().api
get_infrastructure = lambda: github.get_github()


def get_current_user(
    token: str = Depends(oauth.oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_service = jwt.get_jwt()
    try:
        payload = token_service.decode(jwt_token=token)
        uid: str = payload["sub"]
        if uid is None:
            raise credentials_exception
        token_data = TokenData(sub=uid)
        uid = token_data.sub
    except:
        raise credentials_exception

    db_user = crud.get_user(db=db, uid=uid)
    if db_user is None:
        raise credentials_exception

    return User.from_orm(db_user)


async def get_user_api(
    user: User = Depends(get_current_user),
) -> googleapi.GoogleUserAPI:
    return googleapi.GoogleUserAPI(credentials=user.credentials)
