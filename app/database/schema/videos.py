from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, field_validator

from app.config.settings import settings


class Genre(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class Actor(BaseModel):
    id: int
    name: str
    picture: str | None

    class Config:
        from_attributes = True


class VideoActor(Actor):
    type: str | None
    role: str | None

    class Config:
        from_attributes = True


class Staff(BaseModel):
    id: int
    name: str
    picture: str | None

    class Config:
        from_attributes = True


class VideoStaff(Staff):
    type: str | None

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
    width: int | None
    height: int | None

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
    production: str | None
    country: str | None
    like_count: int
    review_count: int
    view_count: int
    thumbnail: list[VideoThumbnail] = []

    class Config:
        from_attributes = True


class Video(VideoSimple):
    synopsis: str
    genre: list[Genre] = []
    actor: list[VideoActor] = []
    staff: list[VideoStaff] = []
    watch: list[VideoWatch] = []

    class Config:
        from_attributes = True


class VideoReview(BaseModel):
    id: int
    video_id: int
    user_id: int
    user_nickname: str
    user_profile_image: str | None
    title: str
    content: str
    like_count: int
    is_spoiler: bool
    created_at: datetime
    updated_at: datetime | None = None

    @field_validator("user_profile_image")
    def image_add_host(cls, value: str) -> str:
        if value is None:
            return value
        return f"{settings.THUMBNAIL_BASE_URL}{value}"

    class Config:
        from_attributes = True


class VideoReviewWithRating(VideoReview):
    rating: int | None

    class Config:
        from_attributes = True


class VideoReviewLike(BaseModel):
    id: int
    review_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class VideoRating(BaseModel):
    id: int
    video_id: int
    user_id: int
    rating: float
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ReqVideoReview(BaseModel):
    title: str
    content: Optional[str] = None
    is_spoiler: Optional[bool] = False
    is_private: Optional[bool] = False

    class Config:
        from_attributes = True


class ResVideo(BaseModel):
    data: Video | None = None


class ResVideos(BaseModel):
    total: int
    count: int
    page: int
    data: List[VideoSimple] | None = None


class ResVideoReview(BaseModel):
    data: VideoReview | None = None


class ResVideoReviews(BaseModel):
    total: int
    count: int
    page: int
    data: List[VideoReview] | None = None


class ResVideoReviewsWithRating(BaseModel):
    total: int
    count: int
    page: int
    data: List[VideoReviewWithRating] | None = None
