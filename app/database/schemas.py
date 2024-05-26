from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class AccessLog(BaseModel):
    id: int
    status: int
    path: str
    ip: str
    user_id: int
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


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


class UserToken(BaseModel):
    id: int
    email: str


class UserDisp(BaseModel):
    id: int
    email: str
    type: str
    nickname: str
    profile_image: str | None = None
    profile: str | None = None
    is_agree: bool = False


class UserMe(UserDisp):
    is_admin: bool
    created_at: datetime
    updated_at: datetime


class UserLogin(UserDisp):
    access_token: str
    refresh_token: str


class Genre(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Actor(BaseModel):
    id: int
    name: str
    picture: str
    profile: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Staff(BaseModel):
    id: int
    name: str
    picture: str
    profile: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoWatch(BaseModel):
    id: int
    type: str
    url: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoThumbnail(BaseModel):
    id: int
    type: str
    url: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Video(BaseModel):
    id: int
    type: str
    title: str
    synopsis: str
    release: str
    runtime: str
    notice_age: str
    grade: float
    like_count: int
    view_count: int
    platform_code: str
    platform_id: str
    is_confirm: bool
    is_delete: bool
    genre: list[Genre] = []
    actor: list[Actor] = []
    staff: list[Staff] = []
    watch: list[VideoWatch] = []
    thumbnail: list[VideoThumbnail] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RequestUserCreate(BaseModel):
    type: str = None
    email: str = None
    password: str = None
    is_active: Optional[bool] = False
    is_agree: Optional[bool] = False
    nickname: Optional[str] = None
    picture: Optional[str] = None
    profile: Optional[str] = None
    token: Optional[str] = None


class RequestUser(BaseModel):
    nickname: str
    password: str
    picture: str
    profile: str
    is_agree: bool


class RequestUserLogin(BaseModel):
    email: str
    password: str


class ReuqestVideo(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    synopsis: Optional[str] = None
    release: Optional[str] = None
    runtime: Optional[str] = None
    notice_age: Optional[str] = None
    platform_code: Optional[str] = None
    platform_id: Optional[str] = None
    is_confirm: Optional[bool] = None
    is_delete: Optional[bool] = None
    genre: Optional[list[Genre]] = []
    actor: Optional[list[Actor]] = []
    staff: Optional[list[Staff]] = []
    watch: Optional[list[VideoWatch]] = []
    thumbnail: Optional[list[VideoThumbnail]] = []


class Videos(BaseModel):
    total: int = 0
    count: int = 0
    page: int = 0
    list: List[Video] = []


class ResponseModel(BaseModel):
    status: str = "success"
    code: str = ""
    message: str = ""


class ResponseUserLogin(ResponseModel):
    data: UserLogin | None = None


class ResponseUserMe(ResponseModel):
    data: UserMe | None = None


class ResponseVideo(ResponseModel):
    data: Video | None = None


class ResponseVideos(ResponseModel):
    data: Videos | None = None





