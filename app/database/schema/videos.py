from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from typing import Sequence

from app.database.schema.default import Res


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
    created_at: datetime
    updated_at: datetime

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


class VideoSimpleAdmin(VideoSimple):
    platform_code: str
    platform_id: str
    is_confirm: bool
    is_delete: bool

    class Config:
        from_attributes = True


class Video(VideoSimple):
    genre: list[Genre] = []
    actor: list[Actor] = []
    staff: list[Staff] = []
    watch: list[VideoWatch] = []

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
    review_count: int
    view_count: int
    platform_code: str
    platform_id: str
    genre: list[GenreAdmin] = []
    actor: list[ActorAdmin] = []
    staff: list[StaffAdmin] = []
    watch: list[VideoWatchAdmin] = []
    thumbnail: list[VideoThumbnailAdmin] = []
    created_at: datetime
    updated_at: datetime

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


class ResVideo(Res):
    data: Video | None = None


class ResVideoAdmin(Res):
    data: VideoAdmin | None = None


class ResVideos(Res):
    total: int
    count: int
    page: int
    data: List[VideoSimple] | None = None


class ResVideosAdmin(Res):
    total: int
    count: int
    page: int
    data: List[VideoSimpleAdmin] | None = None
