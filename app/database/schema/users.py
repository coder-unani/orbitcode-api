from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.database.schema.default import Response


class User(BaseModel):
    id: int
    type: str
    email: str
    password: str
    nickname: str
    profile_image: str
    profile: str
    is_active: bool
    is_admin: bool
    is_agree: bool
    token: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PublicUser(BaseModel):
    id: int
    email: str
    nickname: str
    profile_image: str | None = None


class UserMe(PublicUser):
    type: str
    profile: str | None = None
    is_agree: bool = False
    is_admin: bool = False
    created_at: datetime
    updated_at: datetime | None = None


class UserLogin(BaseModel):
    user: UserMe
    access_token: str
    refresh_token: str


class RequestUserCreate(BaseModel):
    type: str = None
    email: str = None
    password: str = None
    is_agree: Optional[bool] = False
    nickname: Optional[str] = None
    profile_image: Optional[str] = None
    profile: Optional[str] = None


class RequestUser(BaseModel):
    nickname: str
    password: str
    profile_image: str
    profile: str
    is_agree: bool


class RequestUserLogin(BaseModel):
    email: str
    password: str


class RequestUserProfile(BaseModel):
    profile: str


class RequestUserNickname(BaseModel):
    nickname: str


class RequestUserPassword(BaseModel):
    password: str


class RequestUserAgree(BaseModel):
    is_agree: bool


class ResponseUserLogin(Response):
    data: UserLogin | None = None


class ResponseUserMe(Response):
    data: UserMe | None = None
