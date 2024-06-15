from fastapi import APIRouter, Depends, Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.variables import messages
from app.database.database import get_db
from app.database.queryset.users import read_user_by_email, read_user_by_nickname
from app.database.schema.default import ResData
from app.security.validator import validate_email

router = APIRouter()


@router.get("/users/nickname", tags=["validation"], status_code=status.HTTP_204_NO_CONTENT)
async def find_user_by_nickname(
    nickname: str,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    try:
        # 닉네임 파라메터가 없으 호출 된 경우
        if not nickname:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages['VALID_NICK_REQUIRE_ERR'],
                headers={"code": "VALID_NICK_REQUIRE_ERR"}
            )
        # 닉네임으로 회원정보 조회
        user = await read_user_by_nickname(db, nickname)
        # 닉네임 중복 있음
        if user:
            response.headers["code"] = "VALID_NICK_FAIL"
            return None
        # 닉네임 중복 없음
        response.headers["code"] = "VALID_NICK_SUCC"
        return None
    # 예외 발생시
    except HTTPException as e:
        raise e


@router.get("/users/email", tags=["validation"], response_model=ResData)
async def find_user_by_email(
    email: str,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    try:
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages['VALID_EMAIL_REQUIRE_ERR'],
                headers={"code": "VALID_EMAIL_REQUIRE_ERR"}
            )
        validate_code = validate_email(email)
        if validate_code != "VALID_EMAIL_SUCC":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages[validate_code],
                headers={"code": validate_code}
            )
        user = await read_user_by_email(db, email)
        if user:
            response.headers["code"] = "VALID_EMAIL_ALREADY_EXIST"
            return ResData(
                status=status.HTTP_200_OK,
                message=messages['VALID_EMAIL_ALREADY_EXIST'],
                data={"result": True}
            )
        response.headers["code"] = "VALID_EMAIL_SUCC"
        return ResData(
            status=status.HTTP_200_OK,
            message=messages['VALID_EMAIL_SUCC'],
            data={"result": False}
        )
    except HTTPException as e:
        raise e
