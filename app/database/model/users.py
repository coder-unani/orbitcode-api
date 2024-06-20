from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    func,
    ForeignKey,
    Table,
)
from typing import List
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database.database import Base

user_favorite_list = Table(
    "rvvs_user_favorite_list",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("rvvs_user.id")),
    Column("favorite_id", Integer, ForeignKey("rvvs_user_favorite.id")),
)


class User(Base):
    __tablename__ = "rvvs_user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str] = mapped_column(nullable=True)
    nickname: Mapped[str] = mapped_column(nullable=True)
    profile_image: Mapped[str] = mapped_column(nullable=True)
    profile_text: Mapped[str] = mapped_column(nullable=True)
    birth_year: Mapped[int] = mapped_column(nullable=True)
    level: Mapped[int] = mapped_column(default=0)
    mileage: Mapped[int] = mapped_column(default=0)
    like_count: Mapped[int] = mapped_column(default=0)
    review_count: Mapped[int] = mapped_column(default=0)
    rating_count: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_block: Mapped[bool] = mapped_column(default=False)
    is_email_verify: Mapped[bool] = mapped_column(default=False)
    is_privacy_agree: Mapped[bool] = mapped_column(default=False)
    is_terms_agree: Mapped[bool] = mapped_column(default=False)
    is_age_agree: Mapped[bool] = mapped_column(default=False)
    is_marketing_agree: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    favorite: Mapped["UserFavorite"] = relationship(
        back_populates="user", secondary=user_favorite_list, lazy="selectin"
    )


class UserFavorite(Base):
    __tablename__ = "rvvs_user_favorite"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    is_display: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=func.now()
    )
    user: Mapped[List[User]] = relationship(
        back_populates="favorite", secondary=user_favorite_list, lazy="selectin"
    )


class UserLoginLog(Base):
    __tablename__ = "rvvs_log_user_login"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    status: Mapped[int] = mapped_column(default=0)
    code: Mapped[str] = mapped_column(index=True)
    message: Mapped[str] = mapped_column(nullable=True)
    path: Mapped[str] = mapped_column(nullable=True)
    input_id: Mapped[str] = mapped_column(nullable=True)
    client_ip: Mapped[str] = mapped_column(nullable=True)
    client_host: Mapped[str] = mapped_column(nullable=True)
    user_agent: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=func.now()
    )
