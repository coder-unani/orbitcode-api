from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.database.database import Base


class User(Base):
    __tablename__ = 'rvvs_user'

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
    is_block = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)


class UserLoginLog(Base):
    __tablename__ = 'rvvs_user_login_log'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Integer, default=0)
    path = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    user_id = Column(Integer, nullable=True)
    message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
