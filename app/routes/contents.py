import os
from typing import Union
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import schemas, crud
from app.utils.s3client import S3Client

router = APIRouter()

@router.get("/videos", response_model=schemas.ResContentsVideos)
async def contents_videos(
    page: int = 1, 
    is_delete: bool|None = None, 
    is_confirm: bool|None = None,
    keyword: str|None = None,
    db: Session = Depends(get_db)
):
    # page validation
    if page < 0:
        return {"status": "fail", "message": "Page must be greater than 0"}
    # keyword validation
    if keyword and len(keyword.strip()) < 2:
        return {"status": "fail", "message": "Keyword must be at least 2 characters"}

    # get videos
    total, videos = crud.get_videos(db, page=page, is_delete=is_delete, is_confirm=is_confirm, keyword=keyword)
    if not videos:
        return {"status": "fail", "message": "Videos not found", "total": total, "page": page}

    # return videos
    return {"total": total, "page": page, "data": videos}

@router.get("/videos/{video_id}", response_model=schemas.ResContentsVideo)
async def contents_videos_by_id(video_id: int, db: Session = Depends(get_db)):
    video = crud.get_video_by_id(db, video_id=video_id)

    s3client = S3Client()
    attachs = video.attachs
    for i in range(len(attachs)):
        attachs[i].attach_url = s3client.create_presigned_url(attachs[i].attach_url)
    
    video.attachs = attachs
    s3client.close()

    if not video:
        return {"status": "fail", "message": "Video not found"}
    
    return {"data": video}
