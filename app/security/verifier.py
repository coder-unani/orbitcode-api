from fastapi import Request, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.database.schema.users import User
from app.security.password import Password
from app.security.token import JWTManager
from app.database.database import get_db
from app.database.queryset.users import read_user_by_id


def verify_user(user: dict):
    if not user:
        return False
    return True


def verify_user_email(email: str):
    if not email:
        return False
    return True


def verify_user_password(password: str, hashed_password: str):
    if not password or not hashed_password:
        return False
    if not Password.verify_password(password, hashed_password):
        return False
    return True


def verify_user_active(user: User):
    verify_user(user)
    if not user.is_active:
        return False
    return True


def verify_access_token_user(request: Request, db: Session = Depends(get_db)):
    # 토큰 검증
    try:
        # 토큰 존재 유무 검증
        is_token, code, token = JWTManager.get_access_token(request)
        if not is_token or not token:
            raise HTTPException(
                status_code=401,
                detail="Token is required"
            )
        # 토큰 정합성 검증
        decoded_token = JWTManager.decode_access_token(token)
        if not decoded_token:
            raise HTTPException(
                status_code=401,
                detail="Token is invalid"
            )
        # 토큰 만료 검증
        is_expire = JWTManager.verify_access_token_expire(decoded_token)
        if not is_expire:
            raise HTTPException(
                status_code=401,
                detail="Token is expired"
            )
        # 토큰 유저 검증
        is_user, code, user = read_user_by_id(db, decoded_token['user']['id'])
        if not is_user or not user:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed"
            )
        # 토큰 유저 일치 검증
        user = jsonable_encoder(user)
        if user['email'] != decoded_token['user']['email']:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed"
            )

        return user

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )



