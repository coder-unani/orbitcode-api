from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.database.schema.default import Res


class User(BaseModel):
    id: int
    email: str
    nickname: str
    profile_image: str | None = None

    class Config:
        from_attributes = True


class UserAdmin(User):
    type: str
    profile: str
    is_active: bool
    is_admin: bool
    is_agree: bool
    token: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserMe(User):
    type: str
    profile: str | None = None
    is_agree: bool = False
    is_admin: bool = False
    created_at: datetime


class ReqUserCreate(BaseModel):
    email: str
    password: str
    nickname: str
    profile_image: Optional[str] = None
    profile: Optional[str] = None
    type: Optional[str] = "10"
    is_agree: Optional[bool] = False


class ReqUserUpdate(BaseModel):
    nickname: str
    password: str
    profile_image: str
    profile: str
    is_agree: bool


class ReqUserId(BaseModel):
    id: int


class ReqUserLogin(BaseModel):
    email: str
    password: str


class ReqUserProfile(BaseModel):
    profile: str


class ReqUserNickname(BaseModel):
    nickname: str


class ReqUserPassword(BaseModel):
    password: str


class ReqUserAgree(BaseModel):
    is_agree: bool


class ResUserLogin(Res):
    user: UserMe
    access_token: str
    refresh_token: str


class ResUserMe(Res):
    user: UserMe | None = None
