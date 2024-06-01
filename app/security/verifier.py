import secrets
from fastapi import Request, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.network.response import json_response
from app.utils.formatter import format_datetime
from app.security.password import Password
from app.security.token import JWTManager
from app.database.schema.users import User
from app.database.database import get_db
from app.database.queryset.users import read_user_by_id


def verify_user(user: dict):
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )
    return True


def verify_user_email(email: str):
    if not email:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )
    return True


def verify_user_password(password: str, hashed_password: str):
    if not password or not hashed_password:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )
    if not Password.verify_password(password, hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )
    return True


def verify_user_active(user: User):
    if not verify_user(user) or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )
    return True


def verify_user_unblocked(user: User):
    if not verify_user(user) or user.is_block:
        raise HTTPException(
            status_code=401,
            detail="Blocked account"
        )
    return True


def verify_user_isadmin(user: User):
    if not verify_user(user) or not user.is_admin:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )
    return True


def verify_access_token(request: Request):
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
        if not JWTManager.decode_access_token(token):
            raise HTTPException(
                status_code=401,
                detail="Token is invalid"
            )
        # 토큰 만료 검증
        is_unexpire = JWTManager.verify_access_token_expire(decoded_token)
        if not is_unexpire:
            raise HTTPException(
                status_code=401,
                detail="Token is expired"
            )
        # 결과 출력
        return token
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )


def verify_access_token_user(request: Request, db: Session = Depends(get_db)):
    token = verify_access_token(request)
    # 토큰 검증
    try:
        decoded_token = JWTManager.decode_access_token(token)
        # 토큰 유저 검증
        result, user = read_user_by_id(db, decoded_token['user']['id'])
        if not result:
            return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "EXCEPTION")
        if not user:
            return json_response(status.HTTP_400_BAD_REQUEST, "USER_NOT_FOUND")
        # 토큰 유저 일치 검증
        if not secrets.compare_digest(user.email, decoded_token['user']['email']):
            return json_response(status.HTTP_401_UNAUTHORIZED, "USER_NOT_MATCH")
        # 유저 출력 정보 가공
        if user.created_at:
            user.created_at = format_datetime(user.created_at)
        if user.updated_at:
            user.updated_at = format_datetime(user.updated_at)
        # 결과 출력
        return jsonable_encoder(user)
    except HTTPException as e:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "EXCEPTION")


def verify_access_token_admin(request: Request, db: Session = Depends(get_db)):
    user = verify_access_token_user(request, db)
    # 토큰 검증
    if not user['is_admin']:
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_NOT_ADMIN")
    return user


