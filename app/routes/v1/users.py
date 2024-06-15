from fastapi import APIRouter, Depends, UploadFile, status, Request, Response, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.config.variables import messages
from app.utils.file import File
from app.network.response import json_response
from app.security import validator
from app.security.token import JWTManager
from app.security.password import Password
from app.security.verifier import verify_access_token_user, UserLoginVerifier
from app.database.database import get_db
from app.database.queryset import users as queryset
from app.database.schema.users import (
    UserMe,
    ReqUserCreate, ReqUserUpdate, ReqUserLogin, ReqUserNickname, ReqUserPassword, ReqUserProfile, ReqUserMarketing,
    ReqUserId, ResUser, ResUserMe, ResUserProfile, ResUserLogin, ResUserProfileList
)

router = APIRouter()
tags = "users"


@router.get("/users", tags=[tags], status_code=status.HTTP_200_OK, response_model=ResUserProfileList)
async def search_users(
    p: int = 1,
    ps: int = 20,
    uid: int = 0,
    em: str = None,
    nm: str = None,
    response: Response = None,
    db: AsyncSession = Depends(get_db),
):
    # 유저 정보 가져오기
    total, users = await queryset.read_user(
        db,
        page=p,
        page_size=ps,
        user_id=uid,
        email=em,
        nickname=nm
    )
    if total <= 0 and not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            headers={"code": "USER_READ_NOT_FOUND"},
            detail=messages['USER_READ_NOT_FOUND']
        )
    count = len(users)
    # Response Header code
    response.headers['code'] = "USER_READ_SUCC"
    # 결과 출력
    return ResUserProfileList(
        message=messages["USER_READ_SUCC"],
        data=users,
        total=total,
        count=count
    )


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
    # Response Header code
    response.headers['code'] = "USER_CREATE_SUCC"


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
    # Response Header code
    response.headers['code'] = "USER_READ_SUCC"
    # 결과 출력
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
    # DB 업데이트 실패
    if not result:
        response.headers['code'] = "USER_UPDATE_FAIL"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=messages['USER_UPDATE_FAIL'])
    # Response Header code
    response.headers['code'] = "USER_UPDATE_SUCC"


@router.delete("/users/{user_id}", tags=[tags], status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_me(
    user_id: int,
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 유저 정보 일치 확인
    if user_id != auth_user['id']:
        response.headers['code'] = "USER_NOT_MATCH"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages['USER_NOT_MATCH']
        )
    # 유저 삭제
    result = await queryset.delete_user(db, user_id)
    # 결과 출력
    if not result:
        response.headers['code'] = "USER_DELETE_FAIL"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages['USER_DELETE_FAIL']
        )
    # Response Header code
    response.headers['code'] = "USER_DELETE_SUCC"


@router.patch("/users/{user_id}/nickname", tags=[tags], status_code=status.HTTP_204_NO_CONTENT)
async def patch_user_nickname(
    user_id: int,
    req_user: ReqUserNickname,
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 유저 정보 일치 확인
    if user_id != auth_user['id']:
        response.headers['code'] = "USER_NOT_MATCH"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages['USER_NOT_MATCH'])
    # 닉네임 입력 확인
    if not req_user.nickname:
        response.headers['code'] = "USER_UPDATE_NICKNAME_NOT_FOUND"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages['USER_UPDATE_NICKNAME_NOT_FOUND'])
    # 닉네임 유효성 검사
    valid_code = validator.validate_nickname(req_user.nickname)
    if valid_code != "VALID_NICK_SUCC":
        response.headers['code'] = valid_code
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages[valid_code])
    # 닉네임 중복 체크
    verify_nick_result = await queryset.verify_exist_nickname(db, nickname=req_user.nickname)
    if not verify_nick_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers={"code": "VALID_NICK_ALREADY_EXIST"},
            detail=messages['VALID_NICK_ALREADY_EXIST']
        )
    # 닉네임 업데이트
    result = await queryset.update_user_nickname(db, user_id, req_user.nickname)
    # 결과 출력
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "USER_UPDATE_NICKNAME_FAIL"},
            detail=messages['USER_UPDATE_NICKNAME_FAIL']
        )
    # Response Header code
    response.headers['code'] = "USER_UPDATE_NICKNAME_SUCC"


@router.patch("/users/{user_id}/password", tags=[tags], status_code=status.HTTP_204_NO_CONTENT)
async def patch_user_password(
    user_id: int,
    req_user: ReqUserPassword,
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 유저 정보 일치 확인
    if user_id != auth_user['id']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"code": "USER_NOT_MATCH"},
            detail=messages['USER_NOT_MATCH']
        )
    # 비밀번호 입력 확인
    if not req_user.password_origin or not req_user.password_new:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers={"code": "USER_UPDATE_PASSWORD_NOT_FOUND"},
            detail=messages['USER_UPDATE_PASSWORD_NOT_FOUND']
        )
    # 비밀번호 유효성 검사
    valid_code = validator.validate_password(req_user.password_origin)
    if valid_code != "VALID_PWD_SUCC":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers={"code": valid_code},
            detail=messages[valid_code]
        )
    valid_code = validator.validate_password(req_user.password_new)
    if valid_code != "VALID_PWD_SUCC":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers={"code": valid_code},
            detail=messages[valid_code]
        )
    # 기존 비밀번호 검증
    get_user = await queryset.read_user_by_id(db, user_id)
    if not Password.verify_password(req_user.password_origin, get_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers={"code": "USER_PASSWORD_NOT_MATCH"},
            detail=messages['USER_PASSWORD_NOT_MATCH']
        )
    # 비밀번호 암호화
    req_user.password_new = Password.create_password_hash(req_user.password_new)
    # 비밀번호 업데이트
    result = await queryset.update_user_password(db, user_id=user_id, password=req_user.password_new)
    # 결과 출력
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "USER_UPDATE_PASSWORD_FAIL"},
            detail=messages['USER_UPDATE_PASSWORD_FAIL']
        )
    # Response Header code
    response.headers['code'] = "USER_UPDATE_PASSWORD_SUCC"


@router.patch("/users/{user_id}/profile_image", tags=[tags], status_code=status.HTTP_204_NO_CONTENT)
async def patch_user_profile_image(
    user_id: int,
    profile_text: str = None,
    profile_image: UploadFile = None,
    request: Request = None,
    response: Response = None,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 유저 정보 일치 확인
    if user_id != auth_user['id']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"code": "USER_NOT_MATCH"},
            detail=messages['USER_NOT_MATCH']
        )
    # 프로필 이미지 입력 확인
    if profile_image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers={"code": "FILE_NOT_FOUND"},
            detail=messages['FILE_NOT_FOUND']
        )
    # 파일 타입 확인
    if profile_image.content_type not in settings.FILE_UPLOAD_TYPE_ALLOWED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers={"code": "FILE_TYPE_ERR"},
            detail=messages['FILE_TYPE_ERR']
        )
    # 파일 읽기
    read_file = await profile_image.read()
    file_path = File.store(settings.FILE_DIR_TEMP, profile_image.filename, read_file)
    # 파일 저장 확인
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers={"code": "FILE_STORE_FAIL"},
            detail=messages['FILE_STORE_FAIL']
        )
    # 파일 닫기
    profile_image.file.close()
    # S3 업로드
    s3_uploaded_file = File.update_to_s3(file_path, settings.AWS_S3_PATH_USER_PROFILE_IMAGE)
    if not s3_uploaded_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers={"code": "FILE_UPLOAD_FAIL"},
            detail=messages['FILE_UPLOAD_FAIL']
        )
    # 프로필 이미지 업데이트
    result = await queryset.update_user_profile_image(db, user_id, s3_uploaded_file)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "USER_UPDATE_PROFILE_IMAGE_FAIL"},
            detail=messages['USER_UPDATE_PROFILE_IMAGE_FAIL']
        )
    # Response Header code
    response.headers['code'] = "USER_UPDATE_PROFILE_SUCC"


@router.patch("/users/{user_id}/profile_text", tags=[tags], status_code=status.HTTP_204_NO_CONTENT)
async def patch_user_profile_text(
    user_id: int,
    req_user: ReqUserProfile,
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 유저 정보 일치 확인
    if user_id != auth_user['id']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"code": "USER_NOT_MATCH"},
            detail=messages['USER_NOT_MATCH']
        )
    # 프로필 텍스트 입력 확인
    if not req_user.profile_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers={"code": "USER_UPDATE_PROFILE_NOT_FOUND"},
            detail=messages['USER_UPDATE_PROFILE_NOT_FOUND']
        )
    # 프로필 텍스트 업데이트
    result = await queryset.update_user_profile_text(db, user_id, req_user.profile_text)
    # 결과 출력
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "USER_UPDATE_PROFILE_FAIL"},
            detail=messages['USER_UPDATE_PROFILE_FAIL']
        )
    # Response Header code
    response.headers['code'] = "USER_UPDATE_PROFILE_SUCC"


@router.patch("/users/{user_id}/marketing", tags=[tags], status_code=status.HTTP_204_NO_CONTENT)
async def patch_user_marketing_agree(
        user_id: int,
        req_user: ReqUserMarketing,
        response: Response,
        db: AsyncSession = Depends(get_db),
        auth_user: UserMe = Depends(verify_access_token_user)
):
    if user_id != auth_user['id']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"code": "USER_NOT_MATCH"},
            detail=messages['USER_NOT_MATCH']
        )
    # 광고수신 동의 입력 확인
    if req_user.is_marketing_agree is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers={"code": "USER_UPDATE_AGREE_NOT_FOUND"},
            detail=messages['USER_UPDATE_AGREE_NOT_FOUND']
        )
    # 광고수신 동의 업데이트
    result = await queryset.update_user_marketing(db, user_id, req_user.is_marketing_agree)
    # 결과 출력
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "USER_UPDATE_MARKETING_AGREE_FAIL"},
            detail=messages['USER_UPDATE_MARKETING_AGREE_FAIL']
        )
    response.headers['code'] = "USER_UPDATE_MARKETING_AGREE_SUCC"


@router.post("/users/login", tags=[tags], status_code=status.HTTP_200_OK, response_model=ResUserLogin)
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