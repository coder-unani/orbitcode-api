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
    profile_text = Column(String, nullable=True)
    birth_year = Column(Integer, nullable=True)
    level = Column(Integer, default=0)
    mileage = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    review_count = Column(Integer, default=0)
    rating_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_block = Column(Boolean, default=False)
    is_email_verify = Column(Boolean, default=False)
    is_privacy_agree = Column(Boolean, default=False)
    is_terms_agree = Column(Boolean, default=False)
    is_marketing_agree = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True)


class UserLoginLog(Base):
    __tablename__ = 'rvvs_log_user_login'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Integer, default=0)
    code = Column(String, nullable=True)
    message = Column(String, nullable=True)
    path = Column(String, nullable=True)
    input_id = Column(Integer, nullable=True)
    client_ip = Column(String, nullable=True)
    client_host = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
