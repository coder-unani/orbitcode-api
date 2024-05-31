from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from typing import Sequence

from app.database.schema.default import Response


class Genre(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class GenreAdmin(Genre):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Actor(BaseModel):
    id: int
    name: str
    picture: str
    profile: str

    class Config:
        from_attributes = True


class ActorAdmin(Actor):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Staff(BaseModel):
    id: int
    name: str
    picture: str
    profile: str

    class Config:
        from_attributes = True


class StaffAdmin(Staff):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoWatch(BaseModel):
    id: int
    type: str
    url: str

    class Config:
        from_attributes = True


class VideoWatchAdmin(VideoWatch):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoThumbnail(BaseModel):
    id: int
    type: str
    url: str

    class Config:
        from_attributes = True


class VideoThumbnailAdmin(VideoThumbnail):
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
    rating: float
    like_count: int
    view_count: int
    genre: list[Genre] = []
    actor: list[Actor] = []
    staff: list[Staff] = []
    watch: list[VideoWatch] = []
    thumbnail: list[VideoThumbnail] = []

    class Config:
        from_attributes = True


class VideoAdmin(BaseModel):
    id: int
    type: str
    title: str
    synopsis: str
    release: str
    runtime: str
    notice_age: str
    rating: float
    like_count: int
    view_count: int
    platform_code: str
    platform_id: str
    genre: list[GenreAdmin] = []
    actor: list[ActorAdmin] = []
    staff: list[StaffAdmin] = []
    watch: list[VideoWatchAdmin] = []
    thumbnail: list[VideoThumbnailAdmin] = []

    class Config:
        from_attributes = True


class ReqVideo(BaseModel):
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


class ResVideo(Response):
    data: Video | None = None


class ResVideoAdmin(Response):
    data: VideoAdmin | None = None


class ResVideos(Response):
    total: int
    count: int
    page: int
    data: List[Video] | None = None


class ResVideosAdmin(Response):
    data: List[VideoAdmin] | None = None
