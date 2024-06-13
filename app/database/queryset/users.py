from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import insert, update, delete, exists
from sqlalchemy.future import select

from app.database.model.users import User, UserLoginLog
from app.database.schema.users import UserMe


async def create_user(db: AsyncSession, user: dict):
    try:
        created_user = await db.scalar(insert(User).returning(User), user)
        if created_user:
            await db.commit()
            return True, "USER_CREATE_SUCC"
        else:
            return False, "USER_CREATE_FAIL"
    except Exception as e:
        await db.rollback()
        print(e)
        return False, "EXCEPTION"


async def read_user_by_email(db: AsyncSession, email: str):
    try:
        user: UserMe = await db.scalar(select(User).filter_by(email=email))
        return user
    except Exception as e:
        print(e)
        return None


async def read_user_by_id(db: AsyncSession, user_id: int):
    try:
        user: User = await db.get(User, user_id)
        return True, user
    except Exception as e:
        print(e)
        return False, None


async def update_user(db: AsyncSession, user_id: int, user: dict):
    try:
        await db.scalar(update(User).where(User.id == user_id).values(**user))
        await db.commit()
        return True, "USER_UPDATE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


async def update_user_password(db: AsyncSession, user_id: int, password: str):
    try:
        await db.scalar(update(User).where(User.id == user_id).values(password=password))
        await db.commit()
        return True, "USER_UPDATE_PASSWORD_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


async def update_user_nickname(db: AsyncSession, user_id: int, nickname: str):
    try:
        await db.scalar(update(User).where(User.id == user_id).values(nickname=nickname))
        await db.commit()
        return True, "USER_UPDATE_NICKNAME_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


async def update_user_profile(db: AsyncSession, user_id: int, profile: str):
    try:
        await db.scalar(update(User).where(User.id == user_id).values(profile=profile))
        await db.commit()
        return True, "USER_UPDATE_PROFILE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


async def update_user_profile_image(db: AsyncSession, user_id: int, profile_image: str):
    try:
        await db.scalar(update(User).where(User.id == user_id).values(profile_image=profile_image))
        await db.commit()
        return True, "USER_UPDATE_PROFILE_IMAGE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


async def update_user_isagree(db: AsyncSession, user_id: int, is_agree: bool):
    try:
        await db.scalar(update(User).where(User.id == user_id).values(is_agree=is_agree))
        await db.commit()
        return True, "USER_UPDATE_ISAGREE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


async def delete_user(db: AsyncSession, user_id: int):
    try:
        await db.scalar(delete(User).where(User.id == user_id))
        await db.commit()
        return True, "USER_DELETE_SUCC"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


async def check_exist_email(db: AsyncSession, email: str):
    try:
        is_email = await db.scalar(select(exists().where(User.email == email)))
        if is_email:
            return False, "EMAIL_ALREADY_EXIST"
        return True, "EMAIL_DOES_NOT_EXIST"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


async def check_exist_nickname(db: AsyncSession, nickname: str):
    try:
        is_already_nickname = await db.scalar(select(exists().where(User.nickname == nickname)))
        if is_already_nickname:
            return False, "NICKNAME_ALREADY_EXIST"
        return True, "NICKNAME_DOES_NOT_EXIST"
    except Exception as e:
        print(e)
        return False, "EXCEPTION"


async def insert_user_login_log(
    db: AsyncSession,
    status,
    code,
    path,
    message,
    input_id,
    client_ip,
    client_host,
    user_agent
):
    try:
        stmt = insert(UserLoginLog).values(
            status=status,
            code=code,
            path=path,
            message=message,
            input_id=input_id,
            client_ip=client_ip,
            client_host=client_host,
            user_agent=user_agent
        )
        await db.scalar(stmt)
        await db.commit()
    except Exception as e:
        print(e)


