from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database.schema.default import ResponseModel


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


class ResponseVideo(ResponseModel):
    data: Video | None = None


class ResponseVideos(ResponseModel):
    data: Videos | None = None