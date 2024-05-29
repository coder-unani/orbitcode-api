from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select, insert, update, delete

from app.database.model.reviews import Review
from app.database.queryset.users import read_user_by_id
from app.database.queryset.videos import read_video_by_id


def read_video_review_list(db: Session, video_id: int, page: int = 1):
    unit_per_page = 20
    offset = (page - 1) * unit_per_page
    try:
        total = db.execute(select(func.count(Review.id)).filter_by(video_id=video_id)).scalar()
        stmt = select(Review).filter_by(video_id=video_id).offset(offset).limit(unit_per_page)
        result = db.execute(stmt).scalars().all()
        return True, "REVIEW_READ_LIST_SUCC", total, result
    except Exception as e:
        print(e)
        return False, "EXCEPTION", 0, None


def create_video_review(db: Session, video_id: int, user_id: int, review: dict):
    try:
        result, code, user_in = read_user_by_id(db, user_id)
        if not result or not user_in:
            return False, code
        result, code, video_in = read_video_by_id(db, video_id)
        if not result or not video_in:
            return False, code
        review['video_id'] = video_id
        review['video_title'] = video_in.title
        review['user_id'] = user_id
        review['user_nickname'] = user_in.nickname
        review['user_profile_image'] = user_in.profile_image
        result = db.execute(insert(Review).returning(Review), review).scalar()
        db.commit()
        return True, "REVIEW_CREATE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def read_video_review_by_id(db: Session, review_id: int):
    try:
        review: Review = db.get(Review, review_id)
        return True, "REVIEW_READ_SUCC", review
    except Exception as e:
        print(e)
        return False, "EXCEPTION", None


def update_video_review(db: Session, video_id: int, review_id: int, user_id: int, review: dict):
    try:
        result, code, review_in = read_video_review_by_id(db, review_id)
        if not result or not review:
            return False, code
        if video_id != review_in.video_id:
            return False, "REVIEW_UPDATE_PERMISSION_ERR"
        if user_id != review_in.user_id:
            return False, "REVIEW_UPDATE_PERMISSION_ERR"
        stmt = update(Review).where(Review.id == review_id).values(**review)
        db.execute(stmt)
        db.commit()
        return True, "REVIEW_UPDATE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def delete_video_review(db: Session, video_id: int, review_id: int, user_id: int):
    try:
        result, code, review_in = read_video_review_by_id(db, review_id)
        if not result or not review_in:
            return False, code
        if video_id != review_in.video_id:
            return False, "REVIEW_DELETE_PERMISSION_ERR"
        if user_id != review_in.user_id:
            return False, "REVIEW_DELETE_PERMISSION_ERR"
        stmt = delete(Review).where(Review.id == review_id)
        db.execute(stmt)
        db.commit()
        return True, "REVIEW_DELETE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"
