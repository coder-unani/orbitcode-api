from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select, insert, update, delete

from app.database.model.videos import Video


def create_video(db: Session, video: dict):
    try:
        video_new = db.execute(insert(Video).returning(Video), video).scalar()
        db.commit()
        return True, "VIDEO_CREATE_SUCC", video_new
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def read_video(db: Session, video_id: int):
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


def read_video_list(
        db: Session,
        page: int,
        is_delete: bool | None = None,
        is_confirm: bool | None = None,
        keyword: str | None = None
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
        videos = db.execute(stmt.offset(offset).limit(unit_per_page)).scalars()
        count = len(videos)

        return True, "VIDEO_READ_SUCC", total, count, videos

    except Exception as e:
        print(e)
        return False, "EXCEPTION", 0, 0, []
