from datetime import datetime
from typing import List
from sqlalchemy import (
    Table,
    ForeignKey,
    Column,
    Integer,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.database import Base


class Video(Base):
    __tablename__ = "rvvs_video"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str]
    title: Mapped[str] = mapped_column(index=True)
    synopsis: Mapped[str]
    release: Mapped[str]
    runtime: Mapped[str]
    notice_age: Mapped[str]
    rating: Mapped[float]
    # production: Mapped[str] = mapped_column(nullable=True)
    country: Mapped[str] = mapped_column(nullable=True)
    like_count: Mapped[int] = mapped_column(default=0)
    view_count: Mapped[int] = mapped_column(default=0)
    review_count: Mapped[int] = mapped_column(default=0)
    is_confirm: Mapped[bool] = mapped_column(default=False)
    is_delete: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, server_default=func.now(), onupdate=func.now()
    )
    genre: Mapped[List["Genre"]] = relationship(
        "Genre", secondary="rvvs_video_genre", back_populates="video", lazy="selectin"
    )
    genre_list: Mapped[List["VideoGenre"]] = relationship(
        "VideoGenre", overlaps="genre", order_by="VideoGenre.sort", lazy="selectin"
    )
    actor: Mapped[List["Actor"]] = relationship(
        "Actor", secondary="rvvs_video_actor", back_populates="video", lazy="selectin"
    )
    actor_list: Mapped[List["VideoActor"]] = relationship(
        "VideoActor", overlaps="actor", order_by="VideoActor.sort", lazy="selectin"
    )
    staff: Mapped[List["Staff"]] = relationship(
        "Staff",
        secondary="rvvs_video_staff",
        back_populates="video",
        lazy="selectin",
    )
    staff_list: Mapped[List["VideoStaff"]] = relationship(
        "VideoStaff", overlaps="staff", order_by="VideoStaff.sort", lazy="selectin"
    )
    platform: Mapped[List["VideoPlatform"]] = relationship(
        back_populates="video", order_by="VideoPlatform.code", lazy="selectin"
    )
    thumbnail: Mapped[List["VideoThumbnail"]] = relationship(
        back_populates="video", order_by="VideoThumbnail.code", lazy="selectin"
    )

    class Config:
        from_attributes = True


class Genre(Base):
    __tablename__ = "rvvs_genre"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, server_default=func.now(), onupdate=func.now()
    )
    video: Mapped[List["Video"]] = relationship(
        "Video",
        secondary="rvvs_video_genre",
        overlaps="genre_list",
        back_populates="genre",
        lazy="selectin",
    )


class Actor(Base):
    __tablename__ = "rvvs_actor"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    picture: Mapped[str] = mapped_column(nullable=True)
    profile: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, server_default=func.now(), onupdate=func.now()
    )
    video: Mapped[List["Video"]] = relationship(
        "Video",
        secondary="rvvs_video_actor",
        overlaps="actor_list",
        back_populates="actor",
        lazy="selectin",
    )


class Staff(Base):
    __tablename__ = "rvvs_staff"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    picture: Mapped[str] = mapped_column(nullable=True)
    profile: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, server_default=func.now(), onupdate=func.now()
    )
    video: Mapped[List["Video"]] = relationship(
        "Video",
        secondary="rvvs_video_staff",
        overlaps="staff_list",
        back_populates="staff",
        lazy="selectin",
    )


class VideoGenre(Base):
    __tablename__ = "rvvs_video_genre"

    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rvvs_video.id"), primary_key=True
    )
    genre_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rvvs_genre.id"), primary_key=True
    )
    sort: Mapped[int] = mapped_column(default=99)


class VideoActor(Base):
    __tablename__ = "rvvs_video_actor"

    code: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(nullable=True)
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rvvs_video.id"), primary_key=True
    )
    actor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rvvs_actor.id"), primary_key=True
    )
    sort: Mapped[int] = mapped_column(default=99)


class VideoStaff(Base):
    __tablename__ = "rvvs_video_staff"

    code: Mapped[str] = mapped_column(nullable=True)
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rvvs_video.id"), primary_key=True
    )
    staff_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rvvs_staff.id"), primary_key=True
    )
    sort: Mapped[int] = mapped_column(default=99)


class VideoPlatform(Base):
    __tablename__ = "rvvs_video_platform"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str]
    ext_id: Mapped[str]
    url: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, server_default=func.now(), onupdate=func.now()
    )
    video_id: Mapped[int] = mapped_column(ForeignKey("rvvs_video.id"))
    video: Mapped["Video"] = relationship(back_populates="platform", lazy="selectin")


class VideoThumbnail(Base):
    __tablename__ = "rvvs_video_thumbnail"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str]
    url: Mapped[str]
    extension: Mapped[str]
    size: Mapped[int]
    width: Mapped[int]
    height: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, server_default=func.now(), onupdate=func.now()
    )
    video_id: Mapped[int] = mapped_column(ForeignKey("rvvs_video.id"))
    video: Mapped["Video"] = relationship(back_populates="thumbnail", lazy="selectin")


class VideoLike(Base):
    __tablename__ = "rvvs_video_like"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    video_id: Mapped[int] = mapped_column(nullable=False, index=True)
    video_title: Mapped[str] = mapped_column(nullable=False)
    like_type: Mapped[str] = mapped_column(nullable=False, default="10")
    is_like: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[int] = mapped_column(nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, server_default=func.now(), onupdate=func.now()
    )


class VideoViewLog(Base):
    __tablename__ = "rvvs_log_video_view"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    video_id: Mapped[int] = mapped_column(nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(nullable=True)
    client_ip: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=func.now()
    )


class VideoReview(Base):
    __tablename__ = "rvvs_video_review"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str]
    content: Mapped[str] = mapped_column(nullable=True)
    like_count: Mapped[int] = mapped_column(default=0)
    is_spoiler: Mapped[bool] = mapped_column(default=False)
    is_private: Mapped[bool] = mapped_column(default=False)
    is_block: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[int] = mapped_column(nullable=False, index=True)
    user_nickname: Mapped[str] = mapped_column(nullable=False)
    user_profile_image: Mapped[str] = mapped_column(nullable=False)
    video_id: Mapped[int] = mapped_column(nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, server_default=func.now(), onupdate=func.now()
    )


class VideoReviewLike(Base):
    __tablename__ = "rvvs_video_review_like"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    review_id: Mapped[int] = mapped_column(nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(nullable=False, index=True)
    is_like: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, server_default=func.now(), onupdate=func.now()
    )


class VideoRating(Base):
    __tablename__ = "rvvs_video_rating"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    video_id: Mapped[int] = mapped_column(nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(nullable=False, index=True)
    rating: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, server_default=func.now(), onupdate=func.now()
    )
