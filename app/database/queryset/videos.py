from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import select, insert, update, delete

from app.database.model.videos import (
    Video,
    VideoViewLog
)


def create_video(db: Session, video: dict):
    try:
        video_new = db.execute(insert(Video).returning(Video), video).scalar()
        db.commit()
        return True, "VIDEO_CREATE_SUCC", video_new
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def read_video_by_id(db: Session, video_id: int):
    try:
        video: Video = db.get(Video, video_id)
        return True, "VIDEO_READ_SUCC", video
    except Exception as e:
        print(e)
        return False, "EXCEPTION", None


def update_video(db: Session, video_id: int, video: dict):
    try:
        stmt = update(Video).where(Video.id == video_id).values(**video)
        db.execute(stmt)
        db.commit()
        return True, "VIDEO_UPDATE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def delete_video(db: Session, video_id: int):
    try:
        stmt = delete(Video).where(Video.id == video_id)
        db.execute(stmt)
        db.commit()
        return True, "VIDEO_DELETE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def insert_video_view(db: Session, video_id: int, user_id: int | None = None):
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
    db: Session,
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
