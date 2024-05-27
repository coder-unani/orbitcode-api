from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select, insert, update, delete, exists

from app.database.model.users import User


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
        stmt = select(User).filter_by(email=email)
        user: User = db.execute(stmt).scalar()
        return user
    except Exception as e:
        print(e)
        return None


def read_user_by_id(db: Session, user_id: int):
    try:
        user: User = db.get(User, user_id)
        return True, "", user
    except Exception as e:
        print(e)
        return False, "", None


def update_user(db: Session, user_id: int, user: dict):
    try:
        stmt = update(User).where(User.id == user_id).values(**user)
        db.execute(stmt)
        db.commit()
        return True, "USER_UPDATE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def update_user_password(db: Session, user_id: int, password: str):
    try:
        stmt = update(User).where(User.id == user_id).values(password=password)
        db.execute(stmt)
        db.commit()
        return True, "USER_UPDATE_PASSWORD_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def update_user_nickname(db: Session, user_id: int, nickname: str):
    try:
        stmt = update(User).where(User.id == user_id).values(nickname=nickname)
        db.execute(stmt)
        db.commit()
        return True, "USER_UPDATE_NICKNAME_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def update_user_profile(db: Session, user_id: int, profile: str):
    try:
        stmt = update(User).where(User.id == user_id).values(profile=profile)
        db.execute(stmt)
        db.commit()
        return True, "USER_UPDATE_PROFILE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def update_user_profile_image(db: Session, user_id: int, profile_image: str):
    try:
        stmt = update(User).where(User.id == user_id).values(profile_image=profile_image)
        db.execute(stmt)
        db.commit()
        return True, "USER_UPDATE_PROFILE_IMAGE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def update_user_isagree(db: Session, user_id: int, is_agree: bool):
    try:
        stmt = update(User).where(User.id == user_id).values(is_agree=is_agree)
        db.execute(stmt)
        db.commit()
        return True, "USER_UPDATE_ISAGREE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def delete_user(db: Session, user_id: int):
    try:
        stmt = delete(User).where(User.id == user_id)
        db.execute(stmt)
        db.commit()
        return True, "USER_DELETE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def check_exist_email(db: Session, email: str):
    try:
        stmt = select(exists().where(User.email == email))
        is_email = db.execute(stmt).scalar()
        if is_email:
            return False, "EMAIL_ALREADY_EXIST"
        return True, "EMAIL_DOES_NOT_EXIST"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


def check_exist_nickname(db: Session, nickname: str):
    try:
        stmt = select(exists().where(User.nickname == nickname))
        is_already_nickname = db.execute(stmt).scalar()
        if is_already_nickname:
            return False, "NICKNAME_ALREADY_EXIST"
        return True, "NICKNAME_DOES_NOT_EXIST"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"



