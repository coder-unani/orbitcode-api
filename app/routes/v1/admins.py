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
    ResVideosAdmin,
)

#
from memory_profiler import profile

router = APIRouter()

@profile
@router.get(
    "/videos",
    response_model=ResVideosAdmin,
    dependencies=[Depends(verify_access_token_admin)],
    include_in_schema=False
)
async def admin_content_videos(
    p: int = 1,  # 페이지 번호
    ps: int = 20,  # 페이지 당 데이터 수
    q: str = None,  # 검색 키워드
    t: str = None,  # 비디오 타입
    vid: int = None,  # 비디오 ID
    aid: int = None,  # 배우 ID
    sid: int = None,  # 스태프 ID
    gid: int = None,  # 장르 ID
    pid: str = None,  # 플랫폼 ID
    dl: bool = None,  # 삭제 여부
    cf: bool = None,  # 확인 여부
    ob: str = None,  # 정렬 기준
    db: Session = Depends(get_db)
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
    result, code, total, videos = queryset.search_video_list(
        db,
        page=p,
        page_size=ps,
        type=t,
        keyword=q,
        video_id=vid,
        actor_id=aid,
        staff_id=sid,
        genre_id=gid,
        platform_id=pid,
        is_delete=dl,
        is_confirm=cf,
        order_by=ob
    )

    # 비디오 목록 조회 실패
    if not result:
        return json_response(status.HTTP_500_INTERNAL_SERVER_ERROR, code)
    # 가져온 비디오 컨텐츠 카운트
    count = len(list(videos))
    # 비디오 목록이 없을 경우
    if count < 1:
        return json_response(status.HTTP_200_OK, "VIDEO_NOT_FOUND")
    # 성공 응답 반환
    return {"message": "", "total": total, "count": count, "page": p, "data": videos}


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
