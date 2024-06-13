from fastapi import APIRouter, Depends
from fastapi import status
from sqlalchemy.orm import Session

from app.security.verifier import verify_access_token_admin
from app.network.response import json_response
from app.database.database import get_db
from app.database.queryset import videos as queryset
from app.database.schema.default import Res
from app.database.schema.videos import (
    ReqVideo,
    ResVideoAdmin,
    ResVideosAdmin,
)

router = APIRouter()


@router.get("/videos/{video_id}", tags=['contents'], response_model=ResVideoAdmin)
async def read_video(video_id: int, db: Session = Depends(get_db)):
    result, code, video = queryset.read_video_by_id(db, video_id=video_id)
    if not result:
        return json_response(status.HTTP_500_BAD_REQUEST, code)
    if not video:
        return json_response(status.HTTP_400_BAD_REQUEST, code)

    return ResVideoAdmin(code=code, data=video)


# 비디오 업데이트
@router.put("/videos/{video_id}", tags=['contents'], response_model=Res)
async def update_video(video_id: int, video: ReqVideo, db: Session = Depends(get_db)):
    result, code = queryset.update_video(db, video_id=video_id, video=video)
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)


# 비디오 삭제
@router.delete("/videos/{video_id}", tags=['contents'], response_model=Res)
async def delete_video(video_id: int, db: Session = Depends(get_db)):
    result, code = queryset.delete_video(db, video_id=video_id)
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    return json_response(status.HTTP_200_OK, code)
