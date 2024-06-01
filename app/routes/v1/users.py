from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.utils.formatter import format_datetime
from app.utils.file import File
from app.network.response import json_response
from app.security import verifier, validator
from app.security.token import JWTManager
from app.security.verifier import verify_access_token_user
from app.security.password import Password
from app.database.database import get_db
from app.database.queryset import users as queryset
from app.database.schema.default import Response
from app.database.schema.users import (
    UserMe,
    UserLogin,
    RequestUser,
    RequestUserCreate,
    RequestUserLogin,
    RequestUserProfile,
    RequestUserAgree,
    RequestUserNickname,
    RequestUserPassword,
    ResponseUserMe
)


router = APIRouter()


PREFIX = "/users"
ADMIN_PREFIX = "/admin" + PREFIX


@router.post(PREFIX + "/create", response_model=Response)
async def create_user(
    in_user: RequestUserCreate,
    db: Session = Depends(get_db)
):
    # 이메일 유효성 검사
    valid_result, valid_code = validator.validate_email(in_user.email)
    if not valid_result:
        return json_response(status.HTTP_400_BAD_REQUEST, valid_code)
    # 비밀번호 유효성 검사
    valid_result, valid_code = validator.validate_password(in_user.password)
    if not valid_result:
        return json_response(status.HTTP_400_BAD_REQUEST, valid_code)
    # 닉네임 유효성 검사
    valid_result, valid_code = validator.validate_nickname(in_user.nickname)
    if not valid_result:
        return json_response(status.HTTP_400_BAD_REQUEST, valid_code)
    # 유저 타입 유효성 검사
    valid_result, valid_code = validator.validate_usertype(in_user.type)
    if not valid_result:
        return json_response(status.HTTP_400_BAD_REQUEST, valid_code)
    # 이메일 중복 체크
    check_email_result, check_email_code = queryset.check_exist_email(db, email=in_user.email)
    if not check_email_result:
        return json_response(status.HTTP_400_BAD_REQUEST, check_email_code)
    # 닉네임 중복 체크
    check_nick_result, check_nick_code = queryset.check_exist_nickname(db, nickname=in_user.nickname)
    if not check_nick_result:
        return json_response(status.HTTP_400_BAD_REQUEST, check_nick_code)
    # 비밀번호 암호화
    in_user.password = Password.create_password_hash(in_user.password)
    # 유저 생성
    result, code = queryset.create_user(db, user=jsonable_encoder(in_user))
    # TODO: 유저 생성시 is_activate = False 로 생성 후 이메일 인증 후 is_activate = True 로 변경하여야 함
    # 결과 출력
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_201_CREATED, code)


@router.post(PREFIX + "/login", response_model=UserLogin)
async def login_user(
    in_user: RequestUserLogin,
    db: Session = Depends(get_db)
):
    # 유저 정보 가져오기
    get_user = queryset.read_user_by_email(db, in_user.email)
    # 유저 등록정보 확인
    if not verifier.verify_user(get_user):
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_LOGIN_FAIL")
    # 유저 비밀번호 확인
    if not verifier.verify_user_password(in_user.password, get_user.password):
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_LOGIN_FAIL")
    # 유저 활성화 확인
    if not verifier.verify_user_active(get_user):
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_LOGIN_FAIL")
    # 유저 블럭 체크
    if not verifier.verify_user_unblocked(get_user):
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_BLOCKED")
    # 유저정보 가공
    get_user.created_at = format_datetime(get_user.created_at)
    if get_user.updated_at:
        get_user.updated_at = format_datetime(get_user.updated_at)
    response_user = jsonable_encoder(UserMe(**get_user.__dict__))
    # 토큰 생성
    access_token = JWTManager.create_access_token(response_user)
    refresh_token = JWTManager.create_refresh_token(response_user)
    # 리턴 유저 정보 생성
    response_data = {
        "user": response_user,
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    # 결과 출력
    return json_response(status.HTTP_200_OK, "USER_LOGIN_SUCC", response_data)


@router.post(PREFIX + "/me", response_model=ResponseUserMe)
async def read_user_me(
    db: Session = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 유저 정보 가져오기
    result, get_user = queryset.read_user_by_id(db, auth_user['id'])
    if not result:
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_READ_FAIL")
    response_user = jsonable_encoder(UserMe(**get_user.__dict__))
    # 결과 출력
    return json_response(status.HTTP_200_OK, "USER_READ_SUCC", response_user)


@router.get(PREFIX + "/{user_id}", response_model=ResponseUserMe)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 요청 유저 권한 확인
    if not auth_user['is_admin']:
        return json_response(status.HTTP_401_UNAUTHORIZED, "NO_PERMISSION")
    # 유저 정보 가져오기
    result, get_user = queryset.read_user_by_id(db, user_id)
    if not result:
        return json_response(status.HTTP_401_UNAUTHORIZED, "USER_READ_FAIL")
    # 결과 출력
    return json_response(status.HTTP_200_OK, "USER_READ_SUCC", get_user)


@router.put(PREFIX + "/{user_id}", response_model=Response)
async def update_user(
    user_id: int,
    in_user: RequestUser,
    db: Session = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 유저 정보 입력 확인
    if not in_user:
        return json_response(status.HTTP_400_BAD_REQUEST, "USER_UPDATE_NOT_FOUND")
    # 유저 정보 업데이트
    result, code = queryset.update_user(db, user_id, in_user)
    # 결과 출력
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)


@router.delete(PREFIX + "/{user_id}", response_model=Response)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 유저 삭제
    result, code = queryset.delete_user(db, user_id)
    # 결과 출력
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)


@router.patch(PREFIX + "/{user_id}/password", response_model=Response)
async def update_password(
    user_id: int,
    in_user: RequestUserPassword,
    db: Session = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 비밀번호 입력 확인
    if not in_user.password:
        return json_response(status.HTTP_400_BAD_REQUEST, "USER_UPDATE_PASSWORD_NOT_FOUND")
    # 비밀번호 유효성 검사
    valid_result, valid_code = validator.validate_password(in_user.password)
    if not valid_result:
        return json_response(status.HTTP_400_BAD_REQUEST, valid_code)
    # 비밀번호 암호화
    in_user.password = Password.create_password_hash(in_user.password)
    # 비밀번호 업데이트
    result, code = queryset.update_user_password(db, user_id, in_user.password)
    # 결과 출력
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)


@router.patch(PREFIX + "/{user_id}/nickname", response_model=Response)
async def update_nickname(
    user_id: int,
    in_user: RequestUserNickname,
    db: Session = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 닉네임 입력 확인
    if not in_user.nickname:
        return json_response(status.HTTP_400_BAD_REQUEST, "USER_UPDATE_NICKNAME_NOT_FOUND")
    # 닉네임 유효성 검사
    valid_result, valid_code = validator.validate_nickname(in_user.nickname)
    if not valid_result:
        return json_response(status.HTTP_400_BAD_REQUEST, valid_code)
    # 닉네임 중복 체크
    check_nick_result, check_nick_code = queryset.check_exist_nickname(db, nickname=in_user.nickname)
    if not check_nick_result:
        return json_response(status.HTTP_400_BAD_REQUEST, check_nick_code)
    # 닉네임 업데이트
    result, code = queryset.update_user_nickname(db, user_id, in_user.nickname)
    # 결과 출력
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)


@router.patch(PREFIX + "/{user_id}/profile", response_model=Response)
async def update_profile(
    user_id: int,
    in_user: RequestUserProfile,
    db: Session = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 프로필 입력 확인
    if not in_user.profile:
        return json_response(status.HTTP_400_BAD_REQUEST, "USER_UPDATE_PROFILE_NOT_FOUND")
    # 프로필 업데이트
    result, code = queryset.update_user_profile(db, user_id, in_user.profile)
    # 결과 출력
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)


@router.patch(PREFIX + "/{user_id}/profile/image", response_model=Response)
async def update_profile_image(
    file: UploadFile = None,
    db: Session = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    # 파일 입력 확인
    if not file:
        return json_response(status.HTTP_400_BAD_REQUEST, "FILE_NOT_FOUND")
    # 파일 타입 확인
    if file.content_type not in settings.FILE_UPLOAD_TYPE_ALLOWED:
        return json_response(status.HTTP_400_BAD_REQUEST, "FILE_TYPE_ERR")
    # 파일 읽기
    read_file = await file.read()
    file_path = File.store(settings.FILE_DIR_TEMP, file.filename, read_file)
    # 파일 저장 확인
    if not file_path:
        return json_response(status.HTTP_400_BAD_REQUEST, "FILE_STORE_FAIL")
    # 파일 닫기
    file.file.close()
    # S3 업로드
    s3_uploaded_file = File.update_to_s3(file_path, settings.AWS_S3_PATH_USER_PROFILE_IMAGE)
    if not s3_uploaded_file:
        return json_response(status.HTTP_400_BAD_REQUEST, "FILE_UPLOAD_FAIL")
    result, code = queryset.update_user_profile_image(db, auth_user['id'], s3_uploaded_file)
    # 결과 출력
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)


@router.patch(PREFIX + "/{user_id}/agree", response_model=Response)
async def update_agree(
        user_id: int,
        in_user: RequestUserAgree,
        db: Session = Depends(get_db),
        auth_user: UserMe = Depends(verify_access_token_user)
):
    # 광고수신 동의 입력 확인
    if not in_user.is_agree:
        return json_response(status.HTTP_400_BAD_REQUEST, "USER_UPDATE_AGREE_NOT_FOUND")
    # 광고수신 동의 업데이트
    result, code = queryset.update_user_isagree(db, user_id, in_user.is_agree)
    # 결과 출력
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)
