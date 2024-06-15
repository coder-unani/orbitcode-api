from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import insert, update, delete, exists

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


async def read_user(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    user_id: int = 0,
    email: str = None,
    nickname: str = None,
    order_by: str = None,
):
    unit_per_page = page_size
    offset = (page - 1) * unit_per_page

    try:
        stmt = select(User)
        if user_id:
            stmt = stmt.filter_by(id=user_id)
        elif email:
            stmt = stmt.filter_by(email=email)
        elif nickname:
            stmt = stmt.filter(User.nickname.contains(nickname, autoescape=True))
        elif order_by is not None:
            stmt = stmt.order_by(order_by)
        # total
        total = await db.scalar(select(func.count(User.id)).select_from(User))
        # users
        result = await db.execute(stmt.offset(offset).limit(unit_per_page))
        users = result.scalars().all()
        # 결과 리턴
        return total, users
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
        get_user = await db.scalar(select(User).filter_by(id=user_id))
        if get_user:
            setattr(get_user, 'password', password)
            await db.commit()
            return True
        return False
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages['EXCEPTION'],
            headers={"code": "EXCEPTION"}
        )


async def update_user_nickname(db: AsyncSession, user_id: int, nickname: str):
    try:
        await db.execute(update(User).where(User.id == user_id).values(nickname=nickname))
        await db.commit()
        return True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages['EXCEPTION'],
            headers={"code": "EXCEPTION"}
        )


async def update_user_profile_text(db: AsyncSession, user_id: int, profile_text: str):
    try:
        await db.execute(update(User).where(User.id == user_id).values(profile_text=profile_text))
        await db.commit()
        return True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages['EXCEPTION'],
            headers={"code": "EXCEPTION"}
        )


async def update_user_profile_image(db: AsyncSession, user_id: int, profile_image: str):
    try:
        await db.execute(update(User).where(User.id == user_id).values(profile_image=profile_image))
        await db.commit()
        return True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages['EXCEPTION'],
            headers={"code": "EXCEPTION"}
        )


async def update_user_marketing(db: AsyncSession, user_id: int, is_marketing_agree: bool):
    try:
        await db.execute(update(User).where(User.id == user_id).values(is_marketing_agree=is_marketing_agree))
        await db.commit()
        return True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages['EXCEPTION'],
            headers={"code": "EXCEPTION"}
        )


async def delete_user(db: AsyncSession, user_id: int):
    try:
        # TODO: 바로 삭제 할 지 is_delete=True로 변경 후 일정 기간 후 삭제할 지 고민 필요
        await db.execute(delete(User).where(User.id == user_id))
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


