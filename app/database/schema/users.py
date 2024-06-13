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


class UserMe(User):
    type: str
    profile_text: str | None = None
    birth_yaer: int | None = None
    level: int
    mileage: int
    like_count: int
    review_count: int
    rating_count: int
    is_email_verify: bool
    is_marketing_agree: bool
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class UserAdmin(UserMe):
    is_active: bool
    is_block: bool
    is_privacy_agree: bool
    is_terms_agree: bool

    class Config:
        from_attributes = True


class ReqUserCreate(BaseModel):
    email: str
    password: str
    nickname: str
    is_privacy_agree: bool
    is_terms_agree: bool
    type: Optional[str] = "10"
    profile_image: Optional[str] = None
    profile_text: Optional[str] = None
    is_marketing_agree: Optional[bool] = False


class ReqUserUpdate(BaseModel):
    nickname: Optional[str] = None
    password: Optional[str] = None
    profile_image: Optional[str] = None
    profile: Optional[str] = None
    is_marketing_agree: Optional[bool] = None


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


class ResUserLogin(Res):
    user: UserMe
    access_token: str
    refresh_token: str


class ResUserMe(Res):
    user: UserMe | None = None
