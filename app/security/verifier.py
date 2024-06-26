import secrets
from fastapi import Request, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.config.variables import messages
from app.database.database import get_db
from app.database.schema.users import User
from app.database.queryset.users import read_user_by_id, read_user_by_email, insert_user_login_log
from app.network.response import json_response
from app.security.password import Password
from app.security.token import JWTManager
from app.utils.formatter import format_datetime


security = HTTPBasic()


class UserLoginVerifier:
    def __init__(self, db: AsyncSession, request: Request, user: dict):
        self.db = db
        self.user = user
        self.get_user = None
        self.client_ip = request.headers.get('x-real-ip')
        if not self.client_ip:
            self.client_ip = request.client.host
        self.client_host = request.headers.get('host')
        self.user_agent = request.headers.get('user-agent')

    async def return_user_after_verified(self):
        # 이메일 입력 여부 확인
        if not self.user['email']:
            status_code = status.HTTP_400_BAD_REQUEST
            code = "USER_LOGIN_EMAIL_REQUIRED"
            await self.log_login_attempt(status_code, code)
            raise HTTPException(
                status_code=status_code,
                detail=messages[code],
                headers={"code": code}
            )
        # 비밀번호 입력 여부 확인
        if not self.user['password']:
            status_code = status.HTTP_400_BAD_REQUEST
            code = "USER_LOGIN_PASSWORD_REQUIRED"
            await self.log_login_attempt(status_code, code)
            raise HTTPException(
                status_code=status_code,
                detail=messages[code],
                headers={"code": code}
            )
        # 회원 유형 입력 여부 확인
        if not self.user.get('code'):
            status_code = status.HTTP_400_BAD_REQUEST
            code = "USER_LOGIN_TYPE_REQUIRED"
            await self.log_login_attempt(status_code, code)
            raise HTTPException(
                status_code=status_code,
                detail=messages[code],
                headers={"code": code}
            )
        # 회원 유형 유효성 검사
        if self.user['code'] not in settings.USER_CODE_ALLOW:
            status_code = status.HTTP_401_UNAUTHORIZED
            code = "USER_CODE_ERR"
            await self.log_login_attempt(status_code, code)
            raise HTTPException(
                status_code=status_code,
                detail=messages[code],
                headers={"code": code}
            )
        # 데이터베이스 회원 정보 조회
        await self.get_userdata()
        if not self.get_user:
            status_code = status.HTTP_401_UNAUTHORIZED
            code = "USER_LOGIN_FAIL"
            await self.log_login_attempt(status_code, code)
            raise HTTPException(
                status_code=status_code,
                detail=messages[code],
                headers={"code": code}
            )
        # 약관 동의 여부 확인
        # 개인 정보 수집 동의 확인
        # 만 14세 이상 확인
        if not self.get_user['is_privacy_agree'] or not self.get_user['is_terms_agree'] or not self.get_user['is_age_agree']:
            status_code = status.HTTP_401_UNAUTHORIZED
            code = "USER_LOGIN_AGREE_FAIL"
            await self.log_login_attempt(status_code, code)
            raise HTTPException(
                status_code=status_code,
                detail=messages[code],
                headers={"code": code}
            )
        # 회원 유형별 검증
        # 일반 회원
        if self.user['code'] == "10":
            # 비밀번호 일치 여부 확인
            if not Password.verify_password(self.user['password'], self.get_user['password']):
                status_code = status.HTTP_401_UNAUTHORIZED
                code = "USER_LOGIN_AUTH_FAIL"
                await self.log_login_attempt(status_code, code)
                raise HTTPException(
                    status_code=status_code,
                    detail=messages[code],
                    headers={"code": code}
                )
            # 회원 상태 확인
            if not self.get_user['is_active']:
                status_code = status.HTTP_401_UNAUTHORIZED
                code = "USER_LOGIN_AUTH_FAIL"
                await self.log_login_attempt(status_code, code)
                raise HTTPException(
                    status_code=status_code,
                    detail=messages[code],
                    headers={"code": code}
                )
            # 회원 차단 여부 확인
            if self.get_user['is_block']:
                status_code = status.HTTP_401_UNAUTHORIZED
                code = "USER_BLOCKED"
                await self.log_login_attempt(status_code, code)
                raise HTTPException(
                    status_code=status_code,
                    detail=messages[code],
                    headers={"code": code}
                )
        # 구글 회원
        elif self.user['code'] == "11":
            pass
        # 카카오 회원
        elif self.user['code'] == "12":
            pass
        # 기타
        elif self.user['code'] == "13":
            pass
        # 로그인 성공
        status_code = status.HTTP_200_OK
        code = "USER_LOGIN_SUCC"
        # 성공 로그
        await self.log_login_attempt(status_code, code)
        # 회원 정보 리턴
        return self.get_user

    async def get_userdata(self):
        try:
            self.get_user = await read_user_by_email(self.db, self.user['email'])
            self.get_user = jsonable_encoder(self.get_user)
            return True
        except Exception as e:
            print(e)
            return False

    async def log_login_attempt(self, status_code: int, code: str):
        await insert_user_login_log(
            self.db,
            status_code,
            code,
            "",
            "",
            self.user['email'],
            self.client_ip,
            self.client_host,
            self.user_agent
        )


def verify_user(user: dict):
    if not user:
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_LOGIN_AUTH_FAIL")
    return True


def verify_user_email(email: str):
    if not email:
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_LOGIN_AUTH_FAIL")
    return True


def verify_user_password(password: str, hashed_password: str):
    if not password or not hashed_password:
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_LOGIN_AUTH_FAIL")
    if not Password.verify_password(password, hashed_password):
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_LOGIN_AUTH_FAIL")
    return True


def verify_user_active(user: User):
    if not verify_user(user) or not user.is_active:
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_LOGIN_AUTH_FAIL")
    return True


def verify_user_unblocked(user: User):
    if not verify_user(user) or user.is_block:
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_BLOCKED")
    return True


def verify_user_isadmin(user: User):
    if not verify_user(user) or not user.is_admin:
        return json_response(status.HTTP_401_UNAUTHORIZED, "NO_PERMISSION")
    return True


def verify_access_token(request: Request):
    # 토큰 검증
    try:
        # 토큰 존재 유무 검증
        is_token, code, token = JWTManager.get_access_token(request)
        if not is_token or not token:
            return json_response(status.HTTP_400_BAD_REQUEST, "ACCESS_TOKEN_REQUIRE")
        # 토큰 정합성 검증
        decoded_token = JWTManager.decode_access_token(token)
        if not JWTManager.decode_access_token(token):
            return json_response(status.HTTP_400_BAD_REQUEST, "ACCESS_TOKEN_INVALID")
        # 토큰 만료 검증
        is_unexpire = JWTManager.verify_access_token_expire(decoded_token)
        if not is_unexpire:
            return json_response(status.HTTP_400_BAD_REQUEST, "ACCESS_TOKEN_EXPIRED")
        # 결과 출력
        return token
    except HTTPException as e:
        raise e
    except Exception:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "EXCEPTION")


async def verify_access_token_user(request: Request, db: AsyncSession = Depends(get_db)):
    token = verify_access_token(request)
    # 토큰 검증
    try:
        decoded_token = JWTManager.decode_access_token(token)
        # 토큰 유저 검증
        user = await read_user_by_id(db, decoded_token['user']['id'])
        if not user:
            return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "EXCEPTION")
        if not user:
            return json_response(status.HTTP_400_BAD_REQUEST, "USER_NOT_FOUND")
        # 토큰 유저 일치 검증
        if not secrets.compare_digest(user.email, decoded_token['user']['email']):
            return json_response(status.HTTP_401_UNAUTHORIZED, "USER_NOT_MATCH")
        # 결과 출력
        return jsonable_encoder(user)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages['EXCEPTION'],
            headers={"code": "EXCEPTION"}
        )


def verify_access_docs(credentials: HTTPBasicCredentials = Depends(security)):
    if (
        secrets.compare_digest(credentials.username, settings.DOCS_USER)
        and secrets.compare_digest(credentials.password, settings.DOCS_PASSWORD)
    ):
        return credentials.username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Basic"},
    )
