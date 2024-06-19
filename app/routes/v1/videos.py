from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.variables import messages
from app.security.verifier import verify_access_token_user
from app.network.response import json_response
from app.database.database import get_db
from app.database.queryset import videos as queryset
from app.database.queryset import reviews as review_queryset
from app.database.schema.default import ResData
from app.database.schema.users import UserMe
from app.database.schema.videos import ResVideo, ResVideos
from app.database.schema.reviews import RequestReview, ResponseReviews

router = APIRouter()
tags = "VIDEOS"


# 비디오 목록 조회
@router.get(
    "/videos", tags=[tags], status_code=status.HTTP_200_OK, response_model=ResVideos
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


# 비디오 상세정보 조회
@router.get(
    "/videos/{video_id}",
    tags=[tags],
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
    tags=[tags],
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
                detail=messages["VIDEO_VIEW_INST_FAIL"],
            )
        # Response Header Code
        response.headers["code"] = "VIDEO_VIEW_INST_SUCC"
        # 조회수 증가 성공
        return ResData(data={"view_count": view_count})
    except Exception as e:
        raise e


# 비디오 좋아요 토글
@router.get(
    "/videos/{video_id}/like",
    tags=[tags],
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
                headers={"code": "UNAUTHORIZED_USER"},
                detail=messages["UNAUTHORIZED_USER"],
            )
        is_like = await queryset.toggle_video_like(db, video_id, user_id)
        response.headers["code"] = "VIDEO_LIKE_TOGGLE_SUCC"
        return ResData(data={"is_like": is_like})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


# 비디오 리뷰 조회 (리스트)
@router.get("/videos/{video_id}/reviews", tags=[tags], response_model=ResponseReviews)
async def read_video_review_list(
    video_id: int, page: int = 1, db: AsyncSession = Depends(get_db)
):
    result, code, total, reviews = review_queryset.read_video_review_list(
        db, video_id, page
    )
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    if not reviews:
        return json_response(status.HTTP_400_BAD_REQUEST, code)
    return json_response(
        status.HTTP_200_OK,
        code,
        {"total": total, "page": page, "count": len(reviews), "list": reviews},
    )


# 비디오 리뷰 등록
@router.post("/videos/{video_id}/reviews", tags=[tags])
async def create_video_review(
    video_id: int,
    review: RequestReview,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user),
):
    result, code = review_queryset.create_video_review(
        db, video_id, auth_user["id"], jsonable_encoder(review)
    )
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_201_CREATED, code)


# 비디오 리뷰 수정
@router.put("/videos/{video_id}/reviews/{review_id}", tags=[tags])
async def update_video_review(
    video_id: int,
    review_id: int,
    review: RequestReview,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user),
):
    result, code = review_queryset.update_video_review(
        db, video_id, review_id, auth_user["id"], jsonable_encoder(review)
    )
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)


# 비디오 리뷰 삭제
@router.delete("/videos/{video_id}/reviews/{review_id}", tags=[tags])
async def delete_video_review(
    video_id: int,
    review_id: int,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user),
):
    result, code = review_queryset.delete_video_review(
        db, video_id, review_id, auth_user["id"]
    )
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)
