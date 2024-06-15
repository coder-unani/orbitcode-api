from fastapi import APIRouter, Depends, UploadFile, status, Response, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.settings import settings
from app.config.endpoints import EndpointUsers
from app.config.variables import messages
from app.utils.file import File
from app.network.response import json_response
from app.security import validator
from app.security.token import JWTManager
from app.security.verifier import verify_access_token_user, UserLoginVerifier
from app.security.password import Password
from app.database.database import get_db
from app.database.queryset import users as queryset
from app.database.schema.default import Res
from app.database.schema.users import (
    UserMe,
    ReqUserCreate,
    ReqUserUpdate,
    ReqUserLogin,
    ReqUserProfile,
    ReqUserAgree,
    ReqUserNickname,
    ReqUserPassword,
    ReqUserId,
    ResUser,
    ResUserMe,
    ResUserProfile,
    ResUserLogin
)

router = APIRouter()
tags = "users"


@router.get("/users", tags=[tags], status_code=status.HTTP_200_OK, response_model=ResUser)
async def search_users(
    user_id: int,
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 요청 유저 권한 확인
    if not auth_user['is_admin']:
        return json_response(status.HTTP_401_UNAUTHORIZED, "NO_PERMISSION")
    # 유저 정보 가져오기
    get_user = queryset.read_user_by_id(db, user_id)
    if not get_user:
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_READ_FAIL")
    # 결과 출력
    response.headers['code'] = "USER_READ_SUCC"
    return ResUser(message=messages['USER_READ_SUCC'], data=get_user)


@router.post("/users", tags=[tags], status_code=status.HTTP_201_CREATED)
async def create_user(
    req_user: ReqUserCreate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    # 필수 입력값 체크
    if not req_user.email or not req_user.password or not req_user.nickname:
        return json_response(status.HTTP_400_BAD_REQUEST, "USER_CREATE_REQUIRED_FIELDS")
    # 약관 동의 확인
    if not req_user.is_privacy_agree:
        return json_response(status.HTTP_400_BAD_REQUEST, "USER_AGREE_PRIVACY_REQUIRED")
    # 개인정보 수집 동의 확인
    if not req_user.is_terms_agree:
        return json_response(status.HTTP_400_BAD_REQUEST, "USER_AGREE_TERMS_REQUIRED")
    # 만 14세 이상 확인
    if not req_user.is_age_agree:
        return json_response(status.HTTP_400_BAD_REQUEST, "USER_AGREE_AGE_REQUIRED")
    # 이메일 유효성 검사
    valid_email_code = validator.validate_email(req_user.email)
    if valid_email_code != "VALID_EMAIL_SUCC":
        return json_response(status.HTTP_400_BAD_REQUEST, valid_email_code)
    # 비밀번호 유효성 검사
    valid_pwd_code = validator.validate_password(req_user.password)
    if valid_pwd_code != "VALID_PWD_SUCC":
        return json_response(status.HTTP_400_BAD_REQUEST, valid_pwd_code)
    # 닉네임 유효성 검사
    valid_nick_code = validator.validate_nickname(req_user.nickname)
    if valid_nick_code != "VALID_NICK_SUCC":
        return json_response(status.HTTP_400_BAD_REQUEST, valid_nick_code)
    # 유저 타입 유효성 검사
    valid_type_code = validator.validate_usertype(req_user.type)
    if valid_type_code != "VALID_USER_TYPE_SUCC":
        return json_response(status.HTTP_400_BAD_REQUEST, valid_type_code)
    # 이메일 중복 체크
    verify_email = await queryset.verify_exist_email(db, email=req_user.email)
    if not verify_email:
        return json_response(status.HTTP_400_BAD_REQUEST, "VALID_EMAIL_ALREADY_EXIST")
    # 닉네임 중복 체크
    verify_nick = await queryset.verify_exist_nickname(db, nickname=req_user.nickname)
    if not verify_nick:
        return json_response(status.HTTP_400_BAD_REQUEST, "VALID_NICK_ALREADY_EXIST")
    # 비밀번호 암호화
    req_user.password = Password.create_password_hash(req_user.password)
    # 유저 생성
    result = await queryset.create_user(db, user=req_user)
    # TODO: 유저 생성시 is_email_verify = False 로 생성 후 이메일 인증 후 is_email_verify = True 로 변경하여야 함
    # TODO: 가입 시도 로그 기록 (IP, User-Agent, Host 등) 체크해서 하루 가입 가능 횟수 제한 필요
    # 결과 출력
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "USER_CREATE_FAIL")
    response.headers['code'] = "USER_CREATE_SUCC"
    return None


@router.get("/users/{user_id}", tags=[tags], status_code=status.HTTP_200_OK, response_model=ResUserMe)
async def read_user_me(
    user_id: int,
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 유저 정보 일치 확인
    if user_id != auth_user['id']:
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_NOT_MATCH")
    # 유저 정보 가져오기
    get_user = await queryset.read_user_by_id(db, user_id)
    if not get_user:
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_READ_FAIL")
    # 결과 출력
    response.headers['code'] = "USER_READ_SUCC"
    return ResUserMe(message=messages["USER_READ_SUCC"], data=get_user)


@router.put("/users/{user_id}", tags=[tags], status_code=status.HTTP_204_NO_CONTENT)
async def update_user_me(
    user_id: int,
    req_user: ReqUserUpdate,
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 유저 정보 입력 확인
    if not req_user or not user_id:
        response.headers['code'] = "USER_UPDATE_NOT_FOUND"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages['USER_UPDATE_NOT_FOUND'])
    if user_id != auth_user['id']:
        response.headers['code'] = "USER_NOT_MATCH"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages['USER_NOT_MATCH'])
    result = await queryset.update_user(db, user_id, req_user)
    # 결과 출력
    if not result:
        response.headers['code'] = "USER_UPDATE_FAIL"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=messages['USER_UPDATE_FAIL'])
    response.headers['code'] = "USER_UPDATE_SUCC"
    return None


@router.delete("/users/{user_id}", tags=[tags], status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_me(
    user_id: int,
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    if user_id != auth_user['id']:
        response.headers['code'] = "USER_NOT_MATCH"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages['USER_NOT_MATCH']
        )
    # 유저 삭제
    result = queryset.delete_user(db, user_id)
    # 결과 출력
    if not result:
        response.headers['code'] = "USER_DELETE_FAIL"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages['USER_DELETE_FAIL']
        )
    response.headers['code'] = "USER_DELETE_SUCC"
    return None


@router.patch(EndpointUsers.PATCH_NICKNAME, tags=[tags], response_model=Res)
async def patch_user_nickname(
    user_id: int,
    req_user: ReqUserNickname,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 닉네임 입력 확인
    if not req_user.nickname:
        return json_response(status.HTTP_400_BAD_REQUEST, "USER_UPDATE_NICKNAME_NOT_FOUND")
    # 닉네임 유효성 검사
    valid_result, valid_code = validator.validate_nickname(req_user.nickname)
    if not valid_result:
        return json_response(status.HTTP_400_BAD_REQUEST, valid_code)
    # 닉네임 중복 체크
    check_nick_result, check_nick_code = queryset.check_exist_nickname(db, nickname=req_user.nickname)
    if not check_nick_result:
        return json_response(status.HTTP_400_BAD_REQUEST, check_nick_code)
    # 닉네임 업데이트
    result, code = queryset.update_user_nickname(db, user_id, req_user.nickname)
    # 결과 출력
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)


@router.patch(EndpointUsers.PATCH_PASSWORD, tags=[tags], response_model=Res)
async def patch_user_password(
    user_id: int,
    req_user: ReqUserPassword,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 비밀번호 입력 확인
    if not req_user.password:
        return json_response(status.HTTP_400_BAD_REQUEST, "USER_UPDATE_PASSWORD_NOT_FOUND")
    # 비밀번호 유효성 검사
    valid_result, valid_code = validator.validate_password(req_user.password)
    if not valid_result:
        return json_response(status.HTTP_400_BAD_REQUEST, valid_code)
    # 비밀번호 암호화
    req_user.password = Password.create_password_hash(req_user.password)
    # 비밀번호 업데이트
    result, code = queryset.update_user_password(db, user_id, req_user.password)
    # 결과 출력
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)


@router.patch(EndpointUsers.PATCH_PROFILE, tags=[tags], response_model=Res)
async def patch_user_profile(
    user_id: int,
    req_user: ReqUserProfile,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 프로필 입력 확인
    if not req_user.profile:
        return json_response(status.HTTP_400_BAD_REQUEST, "USER_UPDATE_PROFILE_NOT_FOUND")
    # 프로필 업데이트
    result, code = queryset.update_user_profile(db, user_id, req_user.profile)
    # 결과 출력
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)


@router.patch(EndpointUsers.PATCH_MARKETING, tags=[tags], response_model=Res)
async def patch_user_marketing_agree(
        user_id: int,
        req_user: ReqUserAgree,
        db: AsyncSession = Depends(get_db),
        auth_user: UserMe = Depends(verify_access_token_user)
):
    # 광고수신 동의 입력 확인
    if not req_user.is_agree:
        return json_response(status.HTTP_400_BAD_REQUEST, "USER_UPDATE_AGREE_NOT_FOUND")
    # 광고수신 동의 업데이트
    result, code = queryset.update_user_isagree(db, user_id, req_user.is_agree)
    # 결과 출력
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)


@router.post(EndpointUsers.LOGIN, tags=[tags], status_code=status.HTTP_200_OK, response_model=ResUserLogin)
async def login_user(
    req_user: ReqUserLogin,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    try:
        get_user = await UserLoginVerifier(db, request, jsonable_encoder(req_user)).return_user_after_verified()
    except HTTPException as e:
        raise e
    # 토큰 생성
    access_token = JWTManager.create_access_token(get_user)
    refresh_token = JWTManager.create_refresh_token(get_user)
    # 결과 출력
    response.headers['code'] = "USER_LOGIN_SUCC"
    return ResUserLogin(
        message=messages["USER_LOGIN_SUCC"],
        data=get_user,
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.get("/users/detail", tags=[tags], response_model=ResUserProfile)
async def read_user_detail(
    user: ReqUserId,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    pass