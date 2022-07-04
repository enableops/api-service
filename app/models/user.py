from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    uid: str


class UserCreate(UserBase):
    credentials: str


class User(UserCreate):
    id: int

    class Config:
        orm_mode = True


class UserInfo(UserBase):
    class Config:
        orm_mode = True
