from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import insert, update, delete
from sqlalchemy.future import select
from app.database.model.videos import (
    Video,
    VideoViewLog
)


def create_video(db: AsyncSession, video: dict):
    try:
        video_new = db.execute(insert(Video).returning(Video), video).scalar()
        db.commit()
        return True, "VIDEO_CREATE_SUCC", video_new
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def read_video_by_id(db: AsyncSession, video_id: int):
    try:
        video: Video = db.get(Video, video_id)
        return True, "VIDEO_READ_SUCC", video
    except Exception as e:
        print(e)
        return False, "EXCEPTION", None


def update_video(db: AsyncSession, video_id: int, video: dict):
    try:
        stmt = update(Video).where(Video.id == video_id).values(**video)
        db.execute(stmt)
        db.commit()
        return True, "VIDEO_UPDATE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def delete_video(db: AsyncSession, video_id: int):
    try:
        stmt = delete(Video).where(Video.id == video_id)
        db.execute(stmt)
        db.commit()
        return True, "VIDEO_DELETE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def insert_video_view(db: AsyncSession, video_id: int, user_id: int | None = None):
    try:
        with ((db.begin())):
            if user_id:
                stmt_insert = insert(VideoViewLog).values(video_id=video_id, user_id=user_id)
            else:
                stmt_insert = insert(VideoViewLog).values(video_id=video_id)
            db.add(stmt_insert)
            stmt_update = update(Video).where(Video.id == video_id).values(view_count=Video.view_count + 1).returning(
                Video.view_count
            )
            db.add(stmt_update)
            db.commit()
        view_count = db.execute(select(Video.view_count).where(Video.id == video_id)).scalar()
        return True, "VIDEO_VIEW_INSERT_SUCC", view_count
    except Exception as e:
        print(e)
        return False, "EXCEPTION", -1


def read_video_list(
    db: AsyncSession,
    page: int,
    keyword: str | None = None,
    is_delete: bool = False,
    is_confirm: bool = False,
):
    unit_per_page = 20
    offset = (page - 1) * unit_per_page

    try:
        stmt = select(Video)
        if is_delete is not None:
            stmt = stmt.filter_by(is_delete=is_delete)
        if is_confirm is not None:
            stmt = stmt.filter_by(is_confirm=is_confirm)
        if keyword is not None:
            stmt = stmt.filter(Video.title.contains(keyword, autoescape=True))

        total = db.execute(select(func.count()).select_from(stmt)).scalar()
        result = db.execute(stmt.offset(offset).limit(unit_per_page))
        videos = result.scalars().all()
        return True, "VIDEO_READ_SUCC", total, videos

    except Exception as e:
        print(e)
        return False, "EXCEPTION", 0, 0, []


async def search_video_list(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    video_type: str | None = None,
    keyword: str | None = None,
    video_id: int | None = None,
    actor_id: int | None = None,
    staff_id: int | None = None,
    genre_id: int | None = None,
    platform_id: str | None = None,
    is_delete: bool | None = None,
    is_confirm: bool | None = None,
    order_by: str | None = None,
):
    unit_per_page = page_size
    offset = (page - 1) * unit_per_page

    try:
        stmt = select(Video)
        if video_id is not None:
            stmt = stmt.filter_by(id=video_id)
        if video_type is not None:
            stmt = stmt.filter_by(type=video_type)
        if platform_id is not None:
            stmt = stmt.filter_by(platform_id=platform_id)
        if is_delete is not None:
            stmt = stmt.filter_by(is_delete=is_delete)
        if is_confirm is not None:
            stmt = stmt.filter_by(is_confirm=is_confirm)
        if keyword is not None:
            stmt = stmt.filter(Video.title.contains(keyword, autoescape=True))
        if actor_id is not None:
            stmt = stmt.join(Video.actor).filter_by(id=actor_id)
        if staff_id is not None:
            stmt = stmt.join(Video.staff).filter_by(id=staff_id)
        if genre_id is not None:
            stmt = stmt.join(Video.genre).filter_by(id=genre_id)
        if order_by is not None:
            if order_by == "view_desc":
                stmt = stmt.order_by(Video.view_count.desc())
            elif order_by == "view_asc":
                stmt = stmt.order_by(Video.view_count.asc())
            elif order_by == "like_desc":
                stmt = stmt.order_by(Video.like_count.desc())
            elif order_by == "like_asc":
                stmt = stmt.order_by(Video.like_count.asc())
            elif order_by == "new_desc":
                stmt = stmt.order_by(Video.created_at.desc())
            elif order_by == "new_desc":
                stmt = stmt.order_by(Video.created_at.asc())
            elif order_by == "updated_desc":
                stmt = stmt.order_by(Video.updated_at.desc())
            elif order_by == "updated_asc":
                stmt = stmt.order_by(Video.updated_at.asc())
            elif order_by == "title_desc":
                stmt = stmt.order_by(Video.title.desc())
            elif order_by == "title_asc":
                stmt = stmt.order_by(Video.title.asc())
            elif order_by == "rating_desc":
                stmt = stmt.order_by(Video.rating.desc())
            elif order_by == "rating_asc":
                stmt = stmt.order_by(Video.rating.asc())

        # Total count
        total = await db.scalar(select(func.count()).select_from(stmt))
        result = await db.execute(stmt.offset(offset).limit(unit_per_page))
        videos = result.scalars().all()

        return total, videos

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")



