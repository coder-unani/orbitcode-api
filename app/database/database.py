import contextlib

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config.settings import settings


engine = create_async_engine(
    URL.create(
        drivername=settings.DB_DRIVER,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        username=settings.DB_USER_NAME,
        password=settings.DB_USER_PASSWORD,
    )
)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.bind = engine


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
