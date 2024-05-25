from typing import Annotated
from fastapi import Request, APIRouter, Depends
from fastapi.security import HTTPBearer
from fastapi.encoders import jsonable_encoder
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import queryset
from app.database.schemas import UserMe, ResponseModel, ResponseUserLogin, ResponseUserMe, RequestUserCreate, RequestUserLogin
from app.security.password import Password
from app.security.token import JWTManager, verify_access_user
from app.utils.generator import make_response
from app.utils import validator


router = APIRouter()

# @router.get("/", response_model=List[User])
# async def read_users():
#     return [{"username": "Rick"}, {"username": "Morty"}]


@router.post("/create", response_model=ResponseModel)
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
    if not get_user:
        return make_response(False, "USER_VERIFY_FAIL")
    # 유저 비밀번호 확인
    if not Password.verify_password(user.password, get_user.password):
        return make_response(False, "USER_VERIFY_FAIL")
    # 유저 활성화 확인
    if not get_user.is_active:
        return make_response(False, "USER_VERIFY_FAIL")

    # 토큰 생성
    access_token = JWTManager.create_access_token(jsonable_encoder(get_user))
    refresh_token = JWTManager.create_refresh_token(jsonable_encoder(get_user))

    return_user = {
        "id": get_user.id,
        "email": get_user.email,
        "type": get_user.type,
        "nickname": get_user.nickname,
        "picture": get_user.picture,
        "profile": get_user.profile,
        "is_agree": get_user.is_agree,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    return make_response(True, "USER_VERIFY_SUCC", return_user)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


@router.get("/me")
async def read_user(
    request: Request,
    user: UserMe = Depends(verify_access_user),
    db: Session = Depends(get_db)
):
    return {"status": "success", "message": "User has been read successfully."}


@router.get("/update")
async def update_user():
    return {"status": "success", "message": "User has been updated successfully."}


@router.get("/terminate")
async def delete_user():
    return {"status": "success", "message": "User has been deleted successfully."}