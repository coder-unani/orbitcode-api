from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from app.database.database import get_db
from app.database.models import Video


def read_videos(
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

        total = db.scalar(select(func.count()).select_from(stmt))
        videos = db.scalars(stmt.offset(offset).limit(unit_per_page)).all()
        message = "There is video content. COUNT: {}".format(len(videos))

        return "success", message, total, videos

    except Exception as e:
        return "fail", str(e), 0, []


def create_video(db: Session, video: dict):
    try:
        db.add(Video(**video))
        db.commit()
        return "success", "Video has been created successfully."
    except Exception as e:
        return "fail", str(e)


def read_video(db: Session, video_id: int):
    video: Video = db.get(Video, {"id": video_id})
    return video


def update_video(db: Session, video_id: int, video: dict):
    try:
        db.query(Video).filter(Video.id == video_id).update(video)
        db.commit()
        return "success", "Video has been updated successfully."
    except Exception as e:
        return "fail", str(e)


def delete_video(db: Session, video_id: int):
    try:
        db.query(Video).filter(Video.id == video_id).delete()
        db.commit()
        return "success", "Video has been deleted successfully."
    except Exception as e:
        return "fail", str(e)



