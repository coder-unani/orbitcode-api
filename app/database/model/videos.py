from datetime import datetime
from typing import List
from sqlalchemy import (
    Table, ForeignKey, Column, Integer, String, Float, Boolean, DateTime
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.database import Base


content_video_genre = Table(
    'rvvs_video_genre',
    Base.metadata,
    Column('video_id', Integer, ForeignKey('rvvs_video.id')),
    Column('genre_id', Integer, ForeignKey('rvvs_genre.id'))
)

content_video_actor = Table(
    'rvvs_video_actor',
    Base.metadata,
    Column('video_id', Integer, ForeignKey('rvvs_video.id')),
    Column('actor_id', Integer, ForeignKey('rvvs_actor.id'))
)

content_video_staff = Table(
    'rvvs_video_staff',
    Base.metadata,
    Column('video_id', Integer, ForeignKey('rvvs_video.id')),
    Column('staff_id', Integer, ForeignKey('rvvs_staff.id'))
)


class Video(Base):
    __tablename__ = 'rvvs_video'

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
    platform_code: Mapped[str]
    platform_id: Mapped[str]
    is_confirm: Mapped[bool]
    is_delete: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(nullable=True)
    genre: Mapped[List['Genre']] = relationship(secondary=content_video_genre, back_populates="video")
    actor: Mapped[List['Actor']] = relationship(secondary=content_video_actor, back_populates="video")
    staff: Mapped[List['Staff']] = relationship(secondary=content_video_staff, back_populates="video")
    watch: Mapped[List['VideoWatch']] = relationship(back_populates="video")
    thumbnail: Mapped[List['VideoThumbnail']] = relationship(back_populates="video")

    class Config:
        from_attributes = True


class Genre(Base):
    __tablename__ = 'rvvs_genre'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)
    video: Mapped[List['Video']] = relationship(secondary=content_video_genre, back_populates="genre")


class Actor(Base):
    __tablename__ = 'rvvs_actor'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    picture = Column(String, nullable=True)
    profile = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)
    video: Mapped[List['Video']] = relationship(secondary=content_video_actor, back_populates="actor")


class Staff(Base):
    __tablename__ = 'rvvs_staff'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    picture = Column(String, nullable=True)
    profile = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)
    video: Mapped[List['Video']] = relationship(secondary=content_video_staff, back_populates="staff")


class VideoWatch(Base):
    __tablename__ = 'rvvs_video_watch'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    url = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)
    video_id: Mapped[int] = mapped_column(ForeignKey('rvvs_video.id'))
    video: Mapped['Video'] = relationship(back_populates="watch")


class VideoThumbnail(Base):
    __tablename__ = 'rvvs_video_thumbnail'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    url = Column(String)
    extension = Column(String)
    size = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)
    video_id: Mapped[int] = mapped_column(ForeignKey('rvvs_video.id'))
    video: Mapped['Video'] = relationship(back_populates="thumbnail")


class VideoLikeLog(Base):
    __tablename__ = 'rvvs_video_like_log'

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, nullable=False, index=True)
    video_title = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)


class VideoViewLog(Base):
    __tablename__ = 'rvvs_video_view_log'

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
