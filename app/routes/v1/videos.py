from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.variables import messages
from app.security.verifier import verify_access_token_user
from app.database.database import get_db
from app.database.queryset import videos as queryset
from app.database.queryset.users import read_user_by_id
from app.database.schema.default import ResData
from app.database.schema.users import UserMe
from app.database.schema.videos import (
    ReqVideoReview,
    ResVideo,
    ResVideos,
    ResVideoReviews,
)

router = APIRouter()
tags_video = "VIDEOS"
tags_review = "REVIEWS"
tags_rating = "RATINGS"


# 비디오 목록 조회
@router.get(
    "/videos",
    tags=[tags_video],
    status_code=status.HTTP_200_OK,
    response_model=ResVideos,
)
async def content_videos(
    p: int = 1,  # 페이지 번호
    ps: int = 20,  # 페이지 당 컨텐츠 수
    q: str = None,  # 검색 키워드
    t: str = None,  # 비디오 타입
    vid: int = None,  # 비디오 ID
    aid: int = None,  # 배우 ID
    sid: int = None,  # 스태프 ID
    gid: int = None,  # 장르 ID
    ob: str = None,  # 정렬 기준
    response: Response = None,
    db: AsyncSession = Depends(get_db),
):
    # 비디오 목록 조회
    try:
        # page 파라메터 정합성 체크
        if p and p < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_PAGE"},
                detail=messages["INVALID_PARAM_PAGE"],
            )
        if ps and ps < 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_PAGE_SIZE"},
                detail=messages["INVALID_PARAM_PAGE_SIZE"],
            )
        # type 파라메터 정합성 체크
        if t and len(t) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_TYPE"},
                detail=messages["INVALID_PARAM_TYPE"],
            )
        # keyword 파라메터 정합성 체크
        if q and len(q.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_KEYWORD"},
                detail=messages["INVALID_PARAM_KEYWORD"],
            )
        # order_by 파라메터 정합성 체크
        if ob and ob not in [
            "view_desc",
            "view_asc",
            "like_desc",
            "like_asc",
            "new_desc",
            "new_desc",
            "updated_desc",
            "updated_asc",
            "title_desc",
            "title_asc",
            "rating_desc",
            "rating_asc",
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_ORDER_BY"},
                detail=messages["INVALID_PARAM_ORDER_BY"],
            )
        # 비디오 목록 조회
        total, videos = await queryset.search_video_list(
            db,
            page=p,
            page_size=ps,
            video_type=t,
            keyword=q,
            video_id=vid,
            actor_id=aid,
            staff_id=sid,
            genre_id=gid,
            order_by=ob,
        )
        # 비디오 목록이 없을 경우
        if total <= 0 or not videos:
            response.headers["code"] = "VIDEO_NOT_FOUND"
            response.status_code = status.HTTP_204_NO_CONTENT
            return
        # 가져온 비디오 컨텐츠 카운트
        count = len(list(videos))
        # Response Header Code
        response.headers["code"] = "VIDEO_SEARCH_SUCC"
        # 비디오 목록 반환
        return ResVideos(total=total, count=count, page=p, data=videos)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


# 비디오 상세정보 조회
@router.get(
    "/videos/{video_id}",
    tags=[tags_video],
    status_code=status.HTTP_200_OK,
    response_model=ResVideo,
)
async def read_video(
    video_id: int, response: Response, db: AsyncSession = Depends(get_db)
):
    try:
        if not video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_VIDEO_ID"},
                detail=messages["INVALID_PARAM_VIDEO_ID"],
            )
        video = await queryset.read_video(db, video_id=video_id)
        if not video:
            response.headers["code"] = "VIDEO_NOT_FOUND"
        response.headers["code"] = "VIDEO_READ_SUCC"
        return ResVideo(data=video)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


# 비디오 조회수 증가
@router.get(
    "/videos/{video_id}/view",
    tags=[tags_video],
    status_code=status.HTTP_200_OK,
    response_model=ResData,
)
async def insert_video_view(
    video_id: int,
    user_id: int = None,
    request: Request = None,
    response: Response = None,
    db: AsyncSession = Depends(get_db),
):
    client_ip = request.headers.get("x-real-ip")
    if not client_ip:
        client_ip = request.client.host

    try:
        # 비디오 ID 파라메터 체크
        if not video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_VIDEO_ID"},
                detail=messages["INVALID_PARAM_VIDEO_ID"],
            )
        # 비디오 조회수 증가
        view_count = await queryset.insert_video_view(db, video_id, user_id, client_ip)
        # 조회수 증가 실패
        if view_count <= 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=messages["VIDEO_VIEW_UPDATE_FAIL"],
            )
        # Response Header Code
        response.headers["code"] = "VIDEO_VIEW_UPDATE_SUCC"
        # 조회수 증가 성공
        return ResData(data={"view_count": view_count})
    except Exception as e:
        raise e


# 비디오 좋아요 토글
@router.get(
    "/videos/{video_id}/like",
    tags=[tags_video],
    status_code=status.HTTP_200_OK,
    response_model=ResData,
)
async def toggle_video_like(
    video_id: int,
    user_id: int = None,
    response: Response = None,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user),
):
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_USER_ID"},
                detail=messages["INVALID_PARAM_USER_ID"],
            )
        if not video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_VIDEO_ID"},
                detail=messages["INVALID_PARAM_VIDEO_ID"],
            )
        if user_id != auth_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"code": "USER_NOT_MATCH"},
                detail=messages["USER_NOT_MATCH"],
            )
        is_like = await queryset.toggle_video_like(db, video_id, user_id)
        response.headers["code"] = "VIDEO_LIKE_UPDATE_SUCC"
        return ResData(data={"is_like": is_like})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


# 비디오 리뷰 작성
@router.post(
    "/videos/{video_id}/reviews",
    tags=[tags_review],
    status_code=status.HTTP_201_CREATED,
)
async def create_video_review(
    response: Response,
    video_id: int,
    req_review: ReqVideoReview,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user),
):
    try:
        # 비디오 ID 파라메터 체크
        if not video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_VIDEO_ID"},
                detail=messages["INVALID_PARAM_VIDEO_ID"],
            )
        # 비디오 체크
        video = read_video(db, video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "VIDEO_NOT_FOUND"},
                detail=messages["VIDEO_NOT_FOUND"],
            )
        # 회원정보 가져오기
        get_user = await read_user_by_id(db, auth_user["id"])
        if not get_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "USER_NOT_FOUND"},
                detail=messages["USER_NOT_FOUND"],
            )
        # 리뷰 데이터에 회원정보 추가
        review_dict = req_review.dict()
        review_dict["video_id"] = video_id
        review_dict["user_id"] = get_user.id
        review_dict["user_nickname"] = get_user.nickname
        review_dict["user_profile_image"] = get_user.profile_image
        # 리뷰 작성
        review = await queryset.create_video_review(db, review_dict)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                headers={"code": "REVIEW_CREATE_FAIL"},
                detail=messages["REVIEW_CREATE_FAIL"],
            )
        # Response Header Code
        response.headers["code"] = "REVIEW_CREATE_SUCC"
        # 리뷰 작성 성공
        return
    except Exception as e:
        raise e


# 비디오 리뷰 목록 조회
@router.get(
    "/videos/{video_id}/reviews",
    tags=[tags_review],
    status_code=status.HTTP_200_OK,
    response_model=ResVideoReviews,
)
async def read_video_review_list(
    response: Response,
    video_id: int,
    p: int = 1,
    ps: int = 20,
    db: AsyncSession = Depends(get_db),
):
    try:
        if not video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_VIDEO_ID"},
                detail=messages["INVALID_PARAM_VIDEO_ID"],
            )
        total, reviews = await queryset.read_video_review_list(db, video_id, p, ps)
        if not reviews:
            response.headers["code"] = "REVIEW_NOT_FOUND"
        response.headers["code"] = "REVIEW_READ_SUCC"
        return ResVideoReviews(total=total, count=len(reviews), page=1, data=reviews)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


# 비디오 리뷰 수정
@router.put(
    "/videos/{video_id}/reviews/{review_id}",
    tags=[tags_review],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_video_review(
    response: Response,
    video_id: int,
    review_id: int,
    req_review: ReqVideoReview,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user),
):
    try:
        if not video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_VIDEO_ID"},
                detail=messages["INVALID_PARAM_VIDEO_ID"],
            )
        if not review_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_REVIEW_ID"},
                detail=messages["INVALID_PARAM_REVIEW_ID"],
            )
        get_review = await queryset.read_video_review(db, review_id)
        if not get_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "REVIEW_NOT_FOUND"},
                detail=messages["REVIEW_NOT_FOUND"],
            )
        if video_id != get_review.video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "REVIEW_NOT_MATCH"},
                detail=messages["REVIEW_NOT_MATCH"],
            )
        if auth_user["id"] != get_review.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"code": "USER_NOT_MATCH"},
                detail=messages["USER_NOT_MATCH"],
            )
        review = await queryset.update_video_review(db, review_id, req_review.dict())
        if not review:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                headers={"code": "REVIEW_UPDATE_FAIL"},
                detail=messages["REVIEW_UPDATE_FAIL"],
            )
        response.headers["code"] = "REVIEW_UPDATE_SUCC"
        return
    except Exception as e:
        raise e


# 비디오 리뷰 삭제
@router.delete(
    "/videos/{video_id}/reviews/{review_id}",
    tags=[tags_review],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_video_review(
    response: Response,
    video_id: int,
    review_id: int,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user),
):
    try:
        if not video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_VIDEO_ID"},
                detail=messages["INVALID_PARAM_VIDEO_ID"],
            )
        if not review_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_REVIEW_ID"},
                detail=messages["INVALID_PARAM_REVIEW_ID"],
            )
        get_review = await queryset.read_video_review(db, review_id)
        if not get_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "REVIEW_NOT_FOUND"},
                detail=messages["REVIEW_NOT_FOUND"],
            )
        if video_id != get_review.video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "REVIEW_NOT_MATCH"},
                detail=messages["REVIEW_NOT_MATCH"],
            )
        if auth_user["id"] != get_review.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"code": "USER_NOT_MATCH"},
                detail=messages["USER_NOT_MATCH"],
            )
        review = await queryset.delete_video_review(db, review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                headers={"code": "REVIEW_DELETE_FAIL"},
                detail=messages["REVIEW_DELETE_FAIL"],
            )
        response.headers["code"] = "REVIEW_DELETE_SUCC"
        return
    except Exception as e:
        raise e
