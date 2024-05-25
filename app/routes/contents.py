from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import queryset
from app.database.schemas import ResponseModel, ResponseVideo, ResponseVideos, ReuqestVideo
from app.utils.s3client import S3Client
from app.utils.generator import make_response

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

token: Annotated[str, Depends(oauth2_scheme)]


# 비디오 목록 조회
@router.get("/videos", response_model=ResponseVideos)
async def content_videos(
        page: int = 1,
        is_delete: bool | None = None,
        is_confirm: bool | None = None,
        keyword: str | None = None,
        db: Session = Depends(get_db)
):
    # page validation
    if page < 0:
        return {"status": "fail", "message": "Page must be greater than 0"}
    # keyword validation
    if keyword and len(keyword.strip()) < 2:
        return {"status": "fail", "message": "Keyword must be at least 2 characters"}

    # get videos
    status, code, total, count, videos = queryset.read_videos(db, page, is_delete, is_confirm, keyword)

    # return videos
    data = {"total": total, "count": count, "page": page, "list": videos}
    return make_response(status, code, data)


# 비디오 생성
@router.post("/videos", response_model=ResponseModel)
async def create_video(video: ReuqestVideo, db: Session = Depends(get_db)):
    status, message = queryset.create_video(db, video=jsonable_encoder(video))
    return {"status": status, "message": message}


# 비디오 조회
@router.get("/videos/{video_id}", response_model=ResponseVideo)
async def read_video(video_id: int, db: Session = Depends(get_db)):
    video = queryset.read_video(db, video_id=video_id)

    s3client = S3Client()
    thumbnail = video.thumbnail
    for i in range(len(thumbnail)):
        thumbnail[i].url = s3client.create_presigned_url(thumbnail[i].url)

    video.thumbnail = thumbnail
    s3client.close()

    if not video:
        return {"status": "fail", "message": "Video not found"}

    return {"data": video}


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
