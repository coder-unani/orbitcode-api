from typing import Union
from sqlalchemy import Table, ForeignKey, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship

from pydantic import BaseModel
from app.database.database import Base 

content_video_genre = Table(
    'content_video_genre',
    Base.metadata,
    Column('video_id', Integer, ForeignKey('content_video.id')),
    Column('genre_id', Integer, ForeignKey('content_genre.id'))
)

content_video_actor = Table(
    'content_video_actor',
    Base.metadata,
    Column('video_id', Integer, ForeignKey('content_video.id')),
    Column('actor_id', Integer, ForeignKey('content_actor.id'))
)

content_video_staff = Table(
    'content_video_staff',
    Base.metadata,
    Column('video_id', Integer, ForeignKey('content_video.id')),
    Column('staff_id', Integer, ForeignKey('content_staff.id'))
)


class Video(Base):
    __tablename__ = 'content_video'
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    title = Column(String, index=True)
    synopsis = Column(String)
    release = Column(String)
    runtime = Column(String)
    notice_age = Column(String)
    grade = Column(Float)
    like_count = Column(Integer)
    view_count = Column(Integer)
    platform_code = Column(String)
    platform_id = Column(String)
    is_confirm = Column(Boolean)
    is_delete = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    genre = relationship("Genre", secondary=content_video_genre, back_populates="video")
    actor = relationship("Actor", secondary=content_video_actor, back_populates="video")
    staff = relationship("Staff", secondary=content_video_staff, back_populates="video")
    watch = relationship("VideoWatch", back_populates="video")
    thumbnail = relationship("VideoThumbnail", back_populates="video")


class Genre(Base):
    __tablename__ = 'content_genre'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    video = relationship("Video", secondary=content_video_genre, back_populates="genre")


class Actor(Base):
    __tablename__ = 'content_actor'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    picture = Column(String, nullable=True)
    profile = Column(String, nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    video = relationship("Video", secondary=content_video_actor, back_populates="actor")


class Staff(Base):
    __tablename__ = 'content_staff'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    picture = Column(String, nullable=True)
    profile = Column(String, nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    video = relationship("Video", secondary=content_video_staff, back_populates="staff")


class VideoWatch(Base):
    __tablename__ = 'content_video_watch'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    url = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    video_id = Column(Integer, ForeignKey('content_video.id'))
    video = relationship("Video", back_populates="watch")


class VideoThumbnail(Base):
    __tablename__ = 'content_video_thumbnail'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    url = Column(String)
    extension = Column(String)
    size = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    video_id = Column(Integer, ForeignKey('content_video.id'))
    video = relationship("Video", back_populates="thumbnail")
