import uuid

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.security import verifier, validator
from app.security.verifier import verify_access_token_user
from app.security.password import Password
from app.security.token import JWTManager
from app.utils.generator import make_response
from app.utils.file import File
from app.database.database import get_db
from app.database import queryset
from app.database.schemas import (
    UserMe,
    RequestUserCreate,
    RequestUserLogin,
    ResponseModel,
    ResponseUserLogin,
    ResponseUserMe
)


router = APIRouter()

# @router.get("/", response_model=List[User])
# async def read_users():
#     return [{"username": "Rick"}, {"username": "Morty"}]


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=ResponseModel)
async def create_user(
    user: RequestUserCreate,
    db: Session = Depends(get_db)
):
    # 이메일 유효성 검사
    valid_result, valid_code = validator.validate_email(user.email)
    if not valid_result:
        return make_response(valid_result, valid_code)
    # 비밀번호 유효성 검사
    valid_result, valid_code = validator.validate_password(user.password)
    if not valid_result:
        return make_response(valid_result, valid_code)
    # 닉네임 유효성 검사
    valid_result, valid_code = validator.validate_nickname(user.nickname)
    if not valid_result:
        return make_response(valid_result, valid_code)
    # 유저 타입 유효성 검사
    valid_result, valid_code = validator.validate_usertype(user.type)
    if not valid_result:
        return make_response(valid_result, valid_code)

    # 이메일 중복 체크
    check_email_result, check_email_code = queryset.check_email_already(db, email=user.email)
    if not check_email_result:
        return make_response(check_email_result, check_email_code)

    # 닉네임 중복 체크
    check_nick_result, check_nick_code = queryset.check_nickname_already(db, nickname=user.nickname)
    if not check_nick_result:
        return make_response(check_nick_result, check_nick_code)

    # 비밀번호 암호화
    user.password = Password.create_password_hash(user.password)

    # 유저 생성
    result, code = queryset.create_user(db, user=jsonable_encoder(user))

    # TODO: 유저 생성시 is_activate = False 로 생성 후 이메일 인증 후 is_activate = True 로 변경하여야 함

    # 결과 출력
    return make_response(result, code)


@router.post("/login", response_model=ResponseUserLogin)
async def login_user(
    user: RequestUserLogin,
    db: Session = Depends(get_db)
):
    # 유저 정보 가져오기
    get_user = queryset.read_user_by_email(db, user.email)
    # 유저 등록정보 확인
    if not verifier.verify_user(get_user):
        return make_response(False, "USER_VERIFY_FAIL")
    # 유저 비밀번호 확인
    if not verifier.verify_user_password(user.password, get_user.password):
        return make_response(False, "USER_VERIFY_FAIL")
    # 유저 활성화 확인
    if not verifier.verify_user_active(get_user):
        return make_response(False, "USER_VERIFY_FAIL")
    # 토큰 생성
    access_token = JWTManager.create_access_token(jsonable_encoder(get_user))
    refresh_token = JWTManager.create_refresh_token(jsonable_encoder(get_user))

    return_user = {
        "id": get_user.id,
        "email": get_user.email,
        "type": get_user.type,
        "nickname": get_user.nickname,
        "profile_image": get_user.profile_image,
        "profile": get_user.profile,
        "is_agree": get_user.is_agree,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    return make_response(True, "USER_VERIFY_SUCC", return_user)


@router.get("/me", response_model=ResponseUserMe)
async def read_user(
    user: UserMe = Depends(verify_access_token_user),
):
    result = False
    user_me = dict()
    if user:
        user_me = {
            "id": user['id'],
            "email": user['email'],
            "type": user['type'],
            "nickname": user['nickname'],
            "profile_image": user['profile_image'],
            "profile": user['profile'],
            "is_agree": user['is_agree'],
            "is_admin": user['is_admin'],
            "created_at": user['created_at'],
            "updated_at": user['updated_at'],
        }

    return make_response(result, "USER_READ_SUCC", user_me)


@router.put("/update")
async def update_user():
    return {"status": "success", "message": "User has been updated successfully."}


@router.delete("/terminate")
async def delete_user():
    return {"status": "success", "message": "User has been deleted successfully."}


@router.patch("/{user_id}/password")
async def update_password():
    return {"status": "success", "message": "User password has been updated successfully."}


@router.patch("/{user_id}/nickname")
async def update_nickname():
    return {"status": "success", "message": "User nickname has been updated successfully."}


@router.patch("/{user_id}/profile/image", response_model=ResponseModel)
async def update_profile_image(
    file: UploadFile = None,
    db: Session = Depends(get_db),
    user: UserMe = Depends(verify_access_token_user)
):
    if not file:
        return make_response(False, "FILE_NOT_FOUND")

    if file.content_type not in settings.FILE_UPLOAD_TYPE_ALLOWED:
        return make_response(False, "FILE_TYPE_ERR")

    read_file = await file.read()
    file_path = File.store(settings.FILE_DIR_TEMP, file.filename, read_file)
    if not file_path:
        return make_response(False, "FILE_STORE_FAIL")

    file.file.close()

    s3_uploaded_file = File.update_to_s3(file_path, settings.AWS_S3_PATH_USER_PROFILE_IMAGE)
    if not s3_uploaded_file:
        return False

    result, code = queryset.update_user_profile_image(db, user['id'], s3_uploaded_file)

    return make_response(result, code)


@router.patch("/{user_id}/agree")
async def update_agree():
    return {"status": "success", "message": "User profile has been updated successfully."}


@router.patch("/{user_id}/profile")
async def update_profile():
    return {"status": "success", "message": "User profile has been updated successfully."}