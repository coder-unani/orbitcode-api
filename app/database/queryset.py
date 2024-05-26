from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select, insert, update, delete, exists

from app.database.models import User, Video
from app.database.schemas import RequestUserLogin


def create_user(db: Session, user: dict):
    try:
        created_user = db.execute(insert(User).returning(User), user).scalar()
        if created_user:
            db.commit()
            return True, "USER_CREATE_SUCC"
        else:
            return False, "USER_CREATE_FAIL"
    except Exception as e:
        db.rollback()
        print(e)
        return False, "EXCEPTION"


def read_user_by_email(db: Session, email: str):
    try:
        user: User = db.execute(select(User).filter_by(email=email)).scalar()
        return user
    except Exception as e:
        print(e)
        return None


def read_user_by_id(db: Session, id: int):
    try:
        user: User = db.get(User, id)
        return True, "", user
    except Exception as e:
        print(e)
        return False, "", None


def update_user_profile_image(db: Session, user_id: int, profile_image: str):
    try:
        stmt = update(User).where(User.id == user_id).values(profile_image=profile_image)
        db.execute(stmt)
        db.commit()
        return True, "USER_UPDATE_PROFILE_IMAGE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


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
        count = len(videos)

        return True, "VIDEO_READ_SUCC", total, count, videos

    except Exception as e:
        print(e)
        return False, "EXCEPTION", 0, 0, []


def create_video(db: Session, video: dict):
    try:
        db.add(Video(**video))
        db.commit()
        return True, "VIDEO_CREATE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def read_video(db: Session, video_id: int):
    video: Video = db.get(Video, {"id": video_id})
    return True, video


def update_video(db: Session, video_id: int, video: dict):
    try:
        db.query(Video).filter(Video.id == video_id).update(video)
        db.commit()
        return True, "VIDEO_UPDATE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def delete_video(db: Session, video_id: int):
    try:
        db.query(Video).filter(Video.id == video_id).delete()
        db.commit()
        return True, "VIDEO_DELETE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def check_email_already(db: Session, email: str):
    try:
        stmt = select(exists().where(User.email == email))
        is_already_email = db.execute(stmt).scalar()
        if is_already_email:
            return False, "EMAIL_ALREADY_EXIST"
        return True, "EMAIL_DOES_NOT_EXIST"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def check_nickname_already(db: Session, nickname: str):
    try:
        stmt = select(exists().where(User.nickname == nickname))
        is_already_nickname = db.execute(stmt).scalar()
        if is_already_nickname:
            return False, "NICKNAME_ALREADY_EXIST"
        return True, "NICKNAME_DOES_NOT_EXIST"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"



