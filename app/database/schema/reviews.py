from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database.schema.default import Res


class PublicReview(BaseModel):
    id: int
    title: str
    content: str
    rating: float
    like_count: int
    is_spoiler: bool
    is_expect: bool
    is_private: bool
    user_id: int
    user_profile_image: str
    user_nickname: str
    video_id: int
    video_title: str


class PublicReviews(BaseModel):
    total: int
    count: int
    page: int
    list: List[PublicReview]


class Review(PublicReview):
    is_block: bool
    created_at: datetime
    updated_at: datetime


class RequestReview(BaseModel):
    title: str
    content: Optional[str] = None
    rating: Optional[float] = None
    is_spoiler: Optional[bool] = False
    is_expect: Optional[bool] = False
    is_private: Optional[bool] = False


class RequestReviewLike(BaseModel):
    is_like: bool


class ResponseReview(Res):
    data: PublicReview


class ResponseReviews(Res):
    data: PublicReviews

