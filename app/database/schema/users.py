from fastapi import UploadFile, File
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator

from app.config.settings import settings


class User(BaseModel):
    id: int
    email: str
    nickname: str
    profile_image: str | None = None

    @field_validator("email")
    def mask_email(cls, value: str) -> str:
        """
        이메일 주소의 일부를 별표(*)로 마스킹합니다.
        예: test@example.com -> t**t@e******.com
        """
        user, domain = value.split("@")
        masked_user = user[0] + "*" * (len(user) - 2) + user[-1]
        domain_name, domain_extension = domain.split(".")
        masked_domain = (
            domain_name[0] + "*" * (len(domain_name) - 1) + "." + domain_extension
        )
        return masked_user + "@" + masked_domain

    @field_validator("profile_image")
    def image_add_host(cls, value: str) -> str:
        if value is None:
            return value
        result = f"{settings.THUMBNAIL_BASE_URL}{value}".replace("//", "/")
        return result

    class Config:
        from_attributes = True


class UserProfile(User):
    profile_text: str | None = None
    birth_year: int | None = None
    level: int
    like_count: int
    review_count: int
    rating_count: int
    is_email_verify: bool

    class Config:
        from_attributes = True


class UserMe(UserProfile):
    code: str
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
    code: Optional[str] = "10"
    email: str
    is_privacy_agree: bool
    is_terms_agree: bool
    is_age_agree: bool


class ReqUserId(BaseModel):
    id: int


class ReqUserLogin(BaseModel):
    code: str
    email: str
    password: str


class ReqUserNickname(BaseModel):
    nickname: str


class ReqUserPassword(BaseModel):
    password_origin: str
    password_new: str


class ReqUserProfile(BaseModel):
    profile_text: str


class ReqUserMarketing(BaseModel):
    is_marketing_agree: bool


class ResUser(BaseModel):
    data: User


class ResUserProfile(BaseModel):
    data: UserProfile


class ResUserMe(BaseModel):
    user: UserMe


class ResUserLogin(ResUserMe):
    access_token: str
    refresh_token: str


class ResUserProfileList(BaseModel):
    data: list[UserProfile]
