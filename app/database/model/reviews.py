from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime

from app.database.database import Base


class Review(Base):
    __tablename__ = 'rvvs_review'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    rating = Column(Float, default=0.0)
    like_count = Column(Integer, default=0)
    is_spoiler = Column(Boolean, default=False)
    is_expect = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)
    is_block = Column(Boolean, default=False)
    user_id = Column(Integer)
    user_profile_image = Column(String, nullable=True)
    user_nickname = Column(String)
    video_id = Column(Integer)
    video_title = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)