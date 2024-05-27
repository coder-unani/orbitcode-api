from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.database.database import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    nickname = Column(String)
    profile_image = Column(String, nullable=True)
    profile = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_agree = Column(Boolean, default=False)
    token = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
