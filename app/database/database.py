import contextlib

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.config.settings import settings


engine = create_engine(
    URL.create(
        drivername=settings.DB_DRIVER,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        username=settings.DB_USER_NAME,
        password=settings.DB_USER_PASSWORD,
    )
)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.bind = engine


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()