from datetime import datetime
from typing import List
from sqlalchemy import (
    Table,
    ForeignKey,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.database import Base


content_video_genre = Table(
    "rvvs_video_genre",
    Base.metadata,
    Column("video_id", Integer, ForeignKey("rvvs_video.id")),
    Column("genre_id", Integer, ForeignKey("rvvs_genre.id")),
)

content_video_actor = Table(
    "rvvs_video_actor",
    Base.metadata,
    Column("video_id", Integer, ForeignKey("rvvs_video.id")),
    Column("actor_id", Integer, ForeignKey("rvvs_actor.id")),
)

content_video_staff = Table(
    "rvvs_video_staff",
    Base.metadata,
    Column("video_id", Integer, ForeignKey("rvvs_video.id")),
    Column("staff_id", Integer, ForeignKey("rvvs_staff.id")),
)


class Video(Base):
    __tablename__ = "rvvs_video"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str]
    title: Mapped[str] = mapped_column(index=True)
    synopsis: Mapped[str]
    release: Mapped[str]
    runtime: Mapped[str]
    notice_age: Mapped[str]
    rating: Mapped[float]
    like_count: Mapped[int]
    view_count: Mapped[int]
    review_count: Mapped[int]
    platform_code: Mapped[str]
    platform_id: Mapped[str]
    is_confirm: Mapped[bool]
    is_delete: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, server_default=func.now(), onupdate=func.now()
    )
    genre: Mapped[List["Genre"]] = relationship(
        secondary=content_video_genre, back_populates="video", lazy="selectin"
    )
    actor: Mapped[List["Actor"]] = relationship(
        secondary=content_video_actor, back_populates="video", lazy="selectin"
    )
    staff: Mapped[List["Staff"]] = relationship(
        secondary=content_video_staff, back_populates="video", lazy="selectin"
    )
    watch: Mapped[List["VideoWatch"]] = relationship(
        back_populates="video", lazy="selectin"
    )
    thumbnail: Mapped[List["VideoThumbnail"]] = relationship(
        back_populates="video", lazy="selectin"
    )

    class Config:
        from_attributes = True


class Genre(Base):
    __tablename__ = "rvvs_genre"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    updated_at = Column(DateTime, nullable=True)
    video: Mapped[List["Video"]] = relationship(
        secondary=content_video_genre, back_populates="genre", lazy="selectin"
    )


class Actor(Base):
    __tablename__ = "rvvs_actor"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    picture = Column(String, nullable=True)
    profile = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    updated_at = Column(DateTime, nullable=True)
    video: Mapped[List["Video"]] = relationship(
        secondary=content_video_actor, back_populates="actor", lazy="selectin"
    )


class Staff(Base):
    __tablename__ = "rvvs_staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    picture = Column(String, nullable=True)
    profile = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    updated_at = Column(DateTime, nullable=True)
    video: Mapped[List["Video"]] = relationship(
        secondary=content_video_staff, back_populates="staff", lazy="selectin"
    )


class VideoWatch(Base):
    __tablename__ = "rvvs_video_watch"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    url = Column(String)
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    updated_at = Column(DateTime, nullable=True)
    video_id: Mapped[int] = mapped_column(ForeignKey("rvvs_video.id"))
    video: Mapped["Video"] = relationship(back_populates="watch", lazy="selectin")


class VideoThumbnail(Base):
    __tablename__ = "rvvs_video_thumbnail"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    url = Column(String)
    extension = Column(String)
    size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    updated_at = Column(
        DateTime, nullable=True, server_default=func.now(), onupdate=func.now()
    )
    video_id: Mapped[int] = mapped_column(ForeignKey("rvvs_video.id"))
    video: Mapped["Video"] = relationship(back_populates="thumbnail", lazy="selectin")


class VideoLike(Base):
    __tablename__ = "rvvs_video_like"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, nullable=False, index=True)
    video_title = Column(String, nullable=False)
    is_like = Column(Boolean, default=False)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    updated_at = Column(
        DateTime, nullable=True, server_default=func.now(), onupdate=func.now()
    )


class VideoViewLog(Base):
    __tablename__ = "rvvs_log_video_view"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=True)
    client_ip = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
