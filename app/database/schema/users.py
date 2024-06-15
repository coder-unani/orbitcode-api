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


class UserProfile(User):
    profile_text: str | None = None
    birth_yaer: int | None = None
    level: int
    like_count: int
    review_count: int
    rating_count: int
    is_email_verify: bool

    class Config:
        from_attributes = True


class UserMe(UserProfile):
    type: str
    mileage: int
    is_marketing_agree: bool
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ReqUserUpdate(BaseModel):
    nickname: Optional[str] = None
    password: Optional[str] = None
    birth_year: Optional[int] = None
    profile_image: Optional[str] = None
    profile_text: Optional[str] = None
    is_marketing_agree: Optional[bool] = None


class ReqUserCreate(ReqUserUpdate):
    type: Optional[str] = "10"
    email: str
    is_privacy_agree: bool
    is_terms_agree: bool
    is_age_agree: bool


class ReqUserId(BaseModel):
    id: int


class ReqUserLogin(BaseModel):
    type: str
    email: str
    password: str


class ReqUserProfile(BaseModel):
    profile_text: str


class ReqUserNickname(BaseModel):
    nickname: str


class ReqUserPassword(BaseModel):
    password: str


class ReqUserAgree(BaseModel):
    is_agree: bool


class ResUser(Res):
    data: User


class ResUserProfile(Res):
    data: UserProfile


class ResUserMe(Res):
    data: UserMe


class ResUserLogin(ResUserMe):
    access_token: str
    refresh_token: str



