from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import insert, update, delete, exists
from sqlalchemy.future import select
from app.config.variables import messages
from app.database.model.users import User, UserLoginLog
from app.database.schema.users import UserMe, ReqUserCreate, ReqUserUpdate


async def create_user(db: AsyncSession, user: ReqUserCreate):
    try:
        created_user = await db.scalar(insert(User).returning(User), user.dict())
        if created_user:
            await db.commit()
            return True
        else:
            return False
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages['EXCEPTION'],
            headers={"code": "EXCEPTION"}
        )


async def read_user_by_email(db: AsyncSession, email: str):
    try:
        user: UserMe = await db.scalar(select(User).filter_by(email=email))
        return user
    except Exception as e:
        print(e)
        return None


async def read_user_by_nickname(db: AsyncSession, nickname: str):
    try:
        user: UserMe = await db.scalar(select(User).filter_by(nickname=nickname))
        return user
    except Exception as e:
        print(e)
        return None


async def read_user_by_id(db: AsyncSession, user_id: int):
    try:
        user: UserMe = await db.scalar(select(User).filter_by(id=user_id))
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages['EXCEPTION'],
            headers={"code": "EXCEPTION"}
        )


async def update_user(db: AsyncSession, user_id: int, user: ReqUserUpdate):
    try:
        # update_values = dict()
        # for key, value in user.dict(exclude_unset=True).items():
        #     if value:
        #         update_values[key] = value
        # stmt = (
        #     update(User).
        #     where(User.id == user_id).
        #     values(update_values).
        #     execution_options(synchronize_session="fetch")
        # )
        # await db.execute(stmt)
        # await db.commit()
        get_user = await db.scalar(select(User).filter_by(id=user_id))
        if get_user:
            for key, value in user.dict(exclude_unset=True).items():
                if value:
                    setattr(get_user, key, value)
            await db.commit()
            return True
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages['EXCEPTION'],
            headers={"code": "EXCEPTION"}
        )


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
        return True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages['EXCEPTION'],
            headers={"code": "EXCEPTION"}
        )


async def verify_exist_email(db: AsyncSession, email: str):
    try:
        user = await db.scalar(select(exists().where(User.email == email)))
        if user:
            return False
        return True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages['EXCEPTION'],
            headers={"code": "EXCEPTION"}
        )


async def verify_exist_nickname(db: AsyncSession, nickname: str):
    try:
        user = await db.scalar(select(exists().where(User.nickname == nickname)))
        if user:
            return False
        return True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages['EXCEPTION'],
            headers={"code": "EXCEPTION"}
        )


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


