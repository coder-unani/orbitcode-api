from typing import Union
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from pydantic import BaseModel
from app.database.database import Base 

class ContentsVideo(Base):
    __tablename__ = 'contents_video'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    synopsis = Column(String)
    release = Column(String)
    notice_age = Column(String)
    runtime = Column(String)
    platform_code = Column(String)
    platform_id = Column(String)
    is_confirm = Column(Boolean)
    is_delete = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    watchs = relationship("ContentsVideoWatch", back_populates="video")
    genres = relationship("ContentsVideoGenre", back_populates="video")
    staffs = relationship("ContentsVideoStaff", back_populates="video")
    attachs = relationship("ContentsVideoAttach", back_populates="video")

class ContentsVideoWatch(Base):
    __tablename__ = 'contents_video_watch'

    id = Column(Integer, primary_key=True, index=True)
    watch_type = Column(String)
    watch_url = Column(String)
    sort = Column(Integer)
    is_delete = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    video_id = Column(Integer, ForeignKey('contents_video.id'))
    video = relationship("ContentsVideo", back_populates="watchs")

class ContentsVideoGenre(Base):
    __tablename__ = 'contents_video_genre'

    id = Column(Integer, primary_key=True, index=True)
    genre = Column(String)
    sort = Column(Integer)
    is_delete = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    video_id = Column(Integer, ForeignKey('contents_video.id'))
    video = relationship("ContentsVideo", back_populates="genres")

class ContentsVideoStaff(Base):
    __tablename__ = 'contents_video_staff'

    id = Column(Integer, primary_key=True, index=True)
    staff_type = Column(String)
    staff_name = Column(String)
    sort = Column(Integer)
    is_delete = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    video_id = Column(Integer, ForeignKey('contents_video.id'))
    video = relationship("ContentsVideo", back_populates="staffs")

class ContentsVideoAttach(Base):
    __tablename__ = 'contents_video_attach'

    id = Column(Integer, primary_key=True, index=True)
    attach_type = Column(String)
    attach_url = Column(String)
    sort = Column(Integer)
    is_delete = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    video_id = Column(Integer, ForeignKey('contents_video.id'))
    video = relationship("ContentsVideo", back_populates="attachs")
