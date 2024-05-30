from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship

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

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    title = Column(String, index=True)
    synopsis = Column(String)
    release = Column(String)
    runtime = Column(String)
    notice_age = Column(String)
    rating = Column(Float)
    like_count = Column(Integer)
    view_count = Column(Integer)
    platform_code = Column(String)
    platform_id = Column(String)
    is_confirm = Column(Boolean)
    is_delete = Column(Boolean)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)
    genre = relationship("Genre", secondary=content_video_genre, back_populates="video")
    actor = relationship("Actor", secondary=content_video_actor, back_populates="video")
    staff = relationship("Staff", secondary=content_video_staff, back_populates="video")
    watch = relationship("VideoWatch", back_populates="video")
    thumbnail = relationship("VideoThumbnail", back_populates="video")


class Genre(Base):
    __tablename__ = 'rvvs_genre'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)
    video = relationship("Video", secondary=content_video_genre, back_populates="genre")


class Actor(Base):
    __tablename__ = 'rvvs_actor'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    picture = Column(String, nullable=True)
    profile = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)
    video = relationship("Video", secondary=content_video_actor, back_populates="actor")


class Staff(Base):
    __tablename__ = 'rvvs_staff'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    picture = Column(String, nullable=True)
    profile = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)
    video = relationship("Video", secondary=content_video_staff, back_populates="staff")


class VideoWatch(Base):
    __tablename__ = 'rvvs_video_watch'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    url = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)
    video_id = Column(Integer, ForeignKey('rvvs_video.id'))
    video = relationship("Video", back_populates="watch")


class VideoThumbnail(Base):
    __tablename__ = 'rvvs_video_thumbnail'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    url = Column(String)
    extension = Column(String)
    size = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)
    video_id = Column(Integer, ForeignKey('rvvs_video.id'))
    video = relationship("Video", back_populates="thumbnail")


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
