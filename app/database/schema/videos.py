from typing import List
from datetime import datetime
from pydantic import BaseModel, field_validator

from app.config.settings import settings
from app.database.schema.default import Res


class Genre(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class Actor(BaseModel):
    id: int
    name: str
    picture: str
    profile: str

    class Config:
        from_attributes = True


class Staff(BaseModel):
    id: int
    name: str
    picture: str
    profile: str

    class Config:
        from_attributes = True


class VideoWatch(BaseModel):
    id: int
    type: str
    url: str

    class Config:
        from_attributes = True


class VideoThumbnail(BaseModel):
    id: int
    type: str
    url: str
    width: int
    height: int

    @field_validator("url")
    def url_add_host(cls, value: str) -> str:
        return f"{settings.THUMBNAIL_BASE_URL}{value}"

    class Config:
        from_attributes = True


class VideoSimple(BaseModel):
    id: int
    type: str
    title: str
    release: str
    runtime: str
    notice_age: str
    rating: float
    like_count: int
    review_count: int
    view_count: int
    thumbnail: list[VideoThumbnail] = []

    class Config:
        from_attributes = True


class Video(VideoSimple):
    genre: list[Genre] = []
    actor: list[Actor] = []
    staff: list[Staff] = []
    watch: list[VideoWatch] = []

    class Config:
        from_attributes = True


class ResVideo(Res):
    data: Video | None = None


class ResVideos(Res):
    total: int
    count: int
    page: int
    data: List[VideoSimple] | None = None
