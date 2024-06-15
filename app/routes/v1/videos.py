from fastapi import APIRouter, Response, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.s3client import S3Client
from app.database.database import get_db
from app.security.verifier import verify_access_token_user
from app.network.response import json_response
from app.database.queryset import videos as queryset
from app.database.queryset import reviews as review_queryset
from app.database.schema.default import Res, ResData
from app.database.schema.users import UserMe
from app.database.schema.videos import (
    ReqVideo,
    ResVideo,
    ResVideos
)
from app.database.schema.reviews import (
    RequestReview,
    ResponseReviews
)


router = APIRouter()


# 비디오 목록 조회
@router.get("/videos", tags=['contents'], response_model=ResVideos)
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
    db: AsyncSession = Depends(get_db)
):
    # page 파라메터 정합성 체크
    if p and p < 1:
        return json_response(status.HTTP_400_BAD_REQUEST, "INVALID_PARAM_PAGE")
    if ps and ps < 5:
        return json_response(status.HTTP_400_BAD_REQUEST, "INVALID_PARAM_PAGE_SIZE")
    # type 파라메터 정합성 체크
    if t and len(t) < 2:
        return json_response(status.HTTP_400_BAD_REQUEST, "INVALID_PARAM_TYPE")
    # keyword 파라메터 정합성 체크
    if q and len(q.strip()) < 2:
        return json_response(status.HTTP_400_BAD_REQUEST, "INVALID_PARAM_KEYWORD")
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
        "rating_asc"
    ]:
        return json_response(status.HTTP_400_BAD_REQUEST, "INVALID_PARAM_ORDER_BY")
    # 비디오 목록 조회
    try:
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
            order_by=ob
        )
    except Exception as e:
        print(e)
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "EXCEPTION")

    # 비디오 목록 조회 실패
    if total <= 0 or not videos:
        return json_response(status.HTTP_404_NOT_FOUND, "VIDEO_NOT_FOUND")
    # 가져온 비디오 컨텐츠 카운트
    count = len(list(videos))
    # 비디오 목록이 없을 경우
    if count < 1:
        return json_response(status.HTTP_200_OK, "VIDEO_NOT_FOUND")
    # 성공 응답 반환
    response.headers['code'] = "VIDEO_SEARCH_SUCC"
    return ResVideos(total=total, count=count, page=p, data=videos)


# 비디오 상세정보 조회
@router.get("/videos/{video_id}", tags=['contents'], response_model=ResVideo)
async def read_video(video_id: int, db: AsyncSession = Depends(get_db)):
    result, code, video = queryset.read_video_by_id(db, video_id=video_id)
    if not result:
        return json_response(status.HTTP_500_BAD_REQUEST, code)
    if not video:
        return json_response(status.HTTP_400_BAD_REQUEST, code)

    s3client = S3Client()
    thumbnail = video.thumbnail
    for i in range(len(thumbnail)):
        thumbnail[i].url = s3client.create_presigned_url(thumbnail[i].url)
    video.thumbnail = thumbnail
    s3client.close()

    return json_response(status.HTTP_200_OK, code, video)


# 비디오 조회
@router.post("/videos/{video_id}/view", tags=['contents'], response_model=ResData)
async def insert_video_view(video_id: int, db: AsyncSession = Depends(get_db)):
    result, code, view_count = queryset.insert_video_view(db, video_id)
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code, {"view_count": view_count})


# 비디오 좋아요 토글
@router.post("/videos/{video_id}/like", tags=['contents'], response_model=Res)
async def toggle_video_like(video_id: int, db: AsyncSession = Depends(get_db), auth_user: UserMe = Depends(verify_access_token_user)):
    # status, code = queryset.toggle_video_like(db, video_id, auth_user['id'])
    # return make_response(status, code)
    pass


# 비디오 리뷰 조회 (리스트)
@router.get("/videos/{video_id}/reviews", tags=['contents'], response_model=ResponseReviews)
async def read_video_review_list(video_id: int, page: int = 1, db: AsyncSession = Depends(get_db)):
    result, code, total, reviews = review_queryset.read_video_review_list(db, video_id, page)
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    if not reviews:
        return json_response(status.HTTP_400_BAD_REQUEST, code)
    return json_response(status.HTTP_200_OK, code, {"total": total, "page": page, "count": len(reviews), "list": reviews})


# 비디오 리뷰 등록
@router.post("/videos/{video_id}/reviews", tags=['contents'], response_model=Res)
async def create_video_review(
    video_id: int,
    review: RequestReview,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    result, code = review_queryset.create_video_review(db, video_id, auth_user['id'], jsonable_encoder(review))
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_201_CREATED, code)


# 비디오 리뷰 수정
@router.put("/videos/{video_id}/reviews/{review_id}", tags=['contents'], response_model=Res)
async def update_video_review(
    video_id: int,
    review_id: int,
    review: RequestReview,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    result, code = review_queryset.update_video_review(db, video_id, review_id, auth_user['id'], jsonable_encoder(review))
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)


# 비디오 리뷰 삭제
@router.delete("/videos/{video_id}/reviews/{review_id}", tags=['contents'], response_model=Res)
async def delete_video_review(
    video_id: int,
    review_id: int,
    db: AsyncSession = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    result, code = review_queryset.delete_video_review(db, video_id, review_id, auth_user['id'])
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)
