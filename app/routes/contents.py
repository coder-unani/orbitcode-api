import os
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params, paginate

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import schemas, crud

router = APIRouter()

@router.get("/videos", response_model=Page[schemas.ResponseContentsVideos])
async def contents_videos(params: Params = Depends(), db: Session = Depends(get_db)):
    videos = crud.get_videos(db)

    if not videos:
        return {"status": "fail", "message": "Videos not found"}

    return {"data": paginate(videos)}

@router.get("/videos/{video_id}", response_model=schemas.ResponseContentsVideo)
async def contents_videos_by_id(video_id: int, db: Session = Depends(get_db)):
    video = crud.get_video_by_id(db, video_id=video_id)

    if not video:
        return {"status": "fail", "message": "Video not found"}
    
    return {"data": video}
