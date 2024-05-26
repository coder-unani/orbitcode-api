import jwt
from typing import Annotated
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.config.settings import settings
from app.database.database import get_db
from app.database.queryset import read_user_by_id


class JWTEncoder:
    @classmethod
    def encode(cls, data: dict, secret_key: str, algorithm: str):
        return jwt.encode(data, secret_key, algorithm)

    @classmethod
    def decode(cls, token: str):
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except Exception as e:
            print(e)
            return None


class JWTManager:
    @classmethod
    def set_token_data(cls, user: dict, expire: float):
        exp = datetime.timestamp(
            datetime.now(settings.TIME_ZONE) + timedelta(minutes=expire)
        )
        data = {
            "user": {
                "id": user['id'],
                "email": user['email']
            },
            "exp": exp
        }
        return data

    @classmethod
    def get_access_token(cls, request: Request):
        authorization = request.headers.get("Authorization")
        schema, token = get_authorization_scheme_param(authorization)
        if schema.lower() != "bearer":
            return False, "ACCESS_TOKEN_REQUIRE", None
        if not token:
            return False, "ACCESS_TOKEN_REQUIRE", None
        return True, "ACCESS_TOKEN_FOUND", token

    @classmethod
    def create_access_token(cls, user: dict):
        data = cls.set_token_data(user, float(settings.ACCESS_TOKEN_EXPIRE_TIME))
        return JWTEncoder.encode(data, settings.SECRET_KEY, settings.ALGORITHM)

    @classmethod
    def create_refresh_token(cls, user: dict):
        data = cls.set_token_data(user, float(settings.REFRESH_TOKEN_EXPIRE_TIME))
        return JWTEncoder.encode(data, settings.SECRET_KEY, settings.ALGORITHM)

    @classmethod
    def decode_access_token(cls, token: str):
        return JWTEncoder.decode(token)

    @classmethod
    def verify_access_token_expire(cls, payload: dict):
        now = datetime.timestamp(datetime.now(settings.TIME_ZONE))
        if payload['exp'] < now:
            return False
        return True

    @classmethod
    def verify_access_token(cls, user: dict, token: str):
        try:
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is required",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            payload = cls.decode_access_token(token)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is wrong",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            if user['email'] != payload['user']['email']:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is invalid",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            return True

        except HTTPException as e:
            raise e





