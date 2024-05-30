from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.utils.s3client import S3Client
from app.utils.generator import make_response
from app.database.database import get_db
from app.security.verifier import verify_access_token_user
from app.database.queryset import videos as queryset
from app.database.queryset import reviews as review_queryset
from app.database.schema.default import ResponseModel, ResponseDataModel
from app.database.schema.users import UserMe
from app.database.schema.videos import (
    ResponsePublicVideo,
    ResponsePublicVideos,
    ReuqestVideo
)
from app.database.schema.reviews import (
    RequestReview,
    ResponseReviews
)


router = APIRouter()


# 비디오 목록 조회
@router.get("/videos", response_model=ResponsePublicVideos)
async def content_videos(
        page: int = 1,
        keyword: str | None = None,
        db: Session = Depends(get_db)
):
    # page validation
    if page < 0:
        return make_response(False, "INVALID_PARAM_PAGE")
    # keyword validation
    if keyword and len(keyword.strip()) < 2:
        return make_response(False, "INVALID_PARAM_KEYWORD")
    # get videos
    status, code, total, videos = queryset.read_video_list(db, page, keyword)
    videos = list(videos)
    count = len(videos)
    if count < 1:
        return make_response(False, "VIDEO_NOT_FOUND")
    # return videos
    data = {"total": total, "count": count, "page": page, "list": videos}
    return make_response(status, code, data)


# 비디오 생성
@router.post("/videos", response_model=ResponseModel)
async def create_video(video: ReuqestVideo, db: Session = Depends(get_db)):
    status, message = queryset.create_video(db, video=jsonable_encoder(video))
    return {"status": status, "message": message}


# 비디오 조회
@router.get("/videos/{video_id}", response_model=ResponsePublicVideo)
async def read_video(video_id: int, db: Session = Depends(get_db)):
    result, code, video = queryset.read_video_by_id(db, video_id=video_id)
    if not result:
        return make_response(result, code)
    if not video:
        return make_response(result, code)

    s3client = S3Client()
    thumbnail = video.thumbnail
    for i in range(len(thumbnail)):
        thumbnail[i].url = s3client.create_presigned_url(thumbnail[i].url)
    video.thumbnail = thumbnail
    s3client.close()

    return make_response(result, code, video)


# 비디오 업데이트
@router.put("/videos/{video_id}", response_model=ResponseModel)
async def update_video(video_id: int, video: ReuqestVideo, db: Session = Depends(get_db)):
    status, message = queryset.update_video(db, video_id=video_id, video=video)
    return {"status": status, "message": message}


# 비디오 삭제
@router.delete("/videos/{video_id}", response_model=ResponseModel)
async def delete_video(video_id: int, db: Session = Depends(get_db)):
    status, message = queryset.delete_video(db, video_id=video_id)
    return {"status": status, "message": message}


# 비디오 조회
@router.post("/videos/{video_id}/view", response_model=ResponseDataModel)
async def insert_video_view(video_id: int, db: Session = Depends(get_db)):
    status, code, view_count = queryset.insert_video_view(db, video_id)
    return make_response(status, code, {"view_count": view_count})


# 비디오 좋아요 토글
@router.post("/videos/{video_id}/like", response_model=ResponseModel)
async def toggle_video_like(video_id: int, db: Session = Depends(get_db), auth_user: UserMe = Depends(verify_access_token_user)):
    # status, code = queryset.toggle_video_like(db, video_id, auth_user['id'])
    # return make_response(status, code)
    pass


# 비디오 리뷰 조회 (리스트)
@router.get("/videos/{video_id}/reviews", response_model=ResponseReviews)
async def read_video_review_list(video_id: int, page: int = 1, db: Session = Depends(get_db)):
    status, code, total, reviews = review_queryset.read_video_review_list(db, video_id, page)
    return make_response(status, code, {"total": total, "page": page, "count": len(reviews), "list": reviews})


# 비디오 리뷰 등록
@router.post("/videos/{video_id}/reviews", response_model=ResponseModel)
async def create_video_review(
    video_id: int,
    review: RequestReview,
    db: Session = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    status, code = review_queryset.create_video_review(db, video_id, auth_user['id'], jsonable_encoder(review))
    return make_response(status, code)


# 비디오 리뷰 수정
@router.put("/videos/{video_id}/reviews/{review_id}", response_model=ResponseModel)
async def update_video_review(
    video_id: int,
    review_id: int,
    review: RequestReview,
    db: Session = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    status, code = review_queryset.update_video_review(db, video_id, review_id, auth_user['id'], jsonable_encoder(review))
    return make_response(status, code)


# 비디오 리뷰 삭제
@router.delete("/videos/{video_id}/reviews/{review_id}", response_model=ResponseModel)
async def delete_video_review(
    video_id: int,
    review_id: int,
    db: Session = Depends(get_db),
    auth_user: UserMe = Depends(verify_access_token_user)
):
    status, code = review_queryset.delete_video_review(db, video_id, review_id, auth_user['id'])
    return make_response(status, code)