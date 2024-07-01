import asyncio
from typing import List
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.variables import messages
from app.security.verifier import verify_access_token_user
from app.database.database import get_db
from app.database.queryset import videos as queryset
from app.database.queryset.users import read_user_by_id
from app.database.schema.default import ResData
from app.database.schema.users import UserMe
from app.database.schema.videos import (
    Video,
    Actor,
    Staff,
    VideoActor,
    VideoStaff,
    VideoReviewWithRating,
    ReqVideoReview,
    ResVideo,
    ResVideos,
    ResVideoReviews,
    ResVideoReviewsWithRating,
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
            video_code=t,
            keyword=q,
            video_id=vid,
            actor_id=aid,
            staff_id=sid,
            genre_id=gid,
            order_by=ob,
        )

        # 가져온 비디오 컨텐츠 카운트
        count = len(list(videos))

        # 비디오 목록이 없을 경우
        if total <= 0 or not videos or count <= 0:
            response.headers["code"] = "VIDEO_NOT_FOUND"
            response.status_code = status.HTTP_204_NO_CONTENT
            return ResVideos(total=total, count=0, page=p, data=[])
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
async def read_video_detail(
    request: Request,
    response: Response,
    video_id: int,
    user_id: int = None,
    db: AsyncSession = Depends(get_db),
):
    try:
        client_ip = request.headers.get("x-real-ip")
        if not client_ip:
            client_ip = request.client.host

        if not video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_VIDEO_ID"},
                detail=messages["INVALID_PARAM_VIDEO_ID"],
            )
        # 비디오 조회수 증가
        try:
            await queryset.insert_video_view(db, video_id, user_id, client_ip)
        except Exception as e:
            print(e)
        # 비디오 상세정보 조회
        try:
            video = await queryset.read_video(db, video_id=video_id)
            if not video:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    headers={"code": "VIDEO_NOT_FOUND"},
                    detail=messages["VIDEO_NOT_FOUND"],
                )
            # 병렬 처리로 배우정보와 스태프정보 가져오기
            actor_tasks = [
                queryset.read_actor(db, actor_map.actor_id)
                for actor_map in video.actor_list
            ]
            staff_tasks = [
                queryset.read_staff(db, staff_map.staff_id)
                for staff_map in video.staff_list
            ]
            actor_results, staff_results = await asyncio.gather(
                asyncio.gather(*actor_tasks), asyncio.gather(*staff_tasks)
            )
            # 배우정보 생성
            actor_list: List[VideoActor] = [
                VideoActor(
                    id=actor_map.actor_id,
                    code=actor_map.code,
                    role=actor_map.role,
                    name=actor.name,
                    picture=actor.picture,
                    sort=actor_map.sort,
                )
                for actor_map, actor in zip(video.actor_list, actor_results)
            ]
            # 스태프정보 생성
            staff_list: List[VideoStaff] = [
                VideoStaff(
                    id=staff_map.staff_id,
                    code=staff_map.code,
                    name=staff.name,
                    picture=staff.picture,
                    sort=staff_map.sort,
                )
                for staff_map, staff in zip(video.staff_list, staff_results)
            ]
            # 반환할 비디오 정보 생성
            return_video = Video(
                id=video.id,
                code=video.code,
                title=video.title,
                release=video.release,
                runtime=video.runtime,
                notice_age=video.notice_age,
                rating=video.rating,
                # production=video.production,
                country=video.country,
                like_count=video.like_count,
                review_count=video.review_count,
                view_count=video.view_count,
                synopsis=video.synopsis,
                genre=video.genre,
                actor=actor_list,
                staff=staff_list,
                platform=video.platform,
                thumbnail=video.thumbnail,
            )
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "VIDEO_NOT_FOUND"},
                detail=messages["VIDEO_NOT_FOUND"],
            )
        # Response Header Code
        response.headers["code"] = "VIDEO_READ_SUCC"
        # 비디오 상세정보 반환
        return ResVideo(data=return_video)
    except Exception as e:
        print(e)
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
@router.post(
    "/videos/{video_id}/like",
    tags=[tags_video],
    status_code=status.HTTP_200_OK,
    response_model=ResData,
)
async def toggle_video_like(
    video_id: int,
    response: Response = None,
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
        is_like = await queryset.toggle_video_like(db, video_id, auth_user["id"])
        like_count = await queryset.update_video_like_count(db, video_id)
        response.headers["code"] = "VIDEO_LIKE_UPDATE_SUCC"
        return ResData(data={"is_like": is_like, "like_count": like_count})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


@router.post(
    "/videos/{video_id}/myinfo",
    tags=[tags_video],
    status_code=status.HTTP_200_OK,
    response_model=ResData,
)
async def read_video_myinfo(
    response: Response,
    video_id: int,
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
        my_is_like = await queryset.read_video_my_is_like(db, video_id, auth_user["id"])
        my_review = await queryset.read_video_my_review(db, video_id, auth_user["id"])
        if my_review:
            disp_review = {
                "id": my_review.id,
                "title": my_review.title,
                # "content": (
                #     my_review.content
                #     if not my_review.is_spoiler and not my_review.is_private
                #     else ""
                # ),
                "content": my_review.content,
                "is_spoiler": my_review.is_spoiler,
                "is_private": my_review.is_private,
            }
        else:
            disp_review = {}

        my_review_like = await queryset.read_video_my_review_like(
            db, video_id, auth_user["id"]
        )
        my_rating = await queryset.read_video_my_rating(db, video_id, auth_user["id"])
        myinfo = {
            "is_like": my_is_like,
            "review": disp_review,
            "review_like": my_review_like,
            "rating": my_rating,
        }
        response.headers["code"] = "VIDEO_MYINFO_READ_SUCC"
        return ResData(data=myinfo)
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
        video = queryset.read_video(db, video_id=video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "VIDEO_NOT_FOUND"},
                detail=messages["VIDEO_NOT_FOUND"],
            )
        get_review = await queryset.read_video_review_by_user(
            db, video_id, auth_user["id"]
        )
        if get_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "REVIEW_ALREADY_EXIST"},
                detail=messages["REVIEW_ALREADY_EXIST"],
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
        # 비디오 리뷰 수량 업데이트
        update = await queryset.update_video_review_count(db, video_id)
        if not update:
            response.headers["code"] = "REVIEW_COUNT_UPDATE_FAIL"
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
    response_model=ResVideoReviewsWithRating,
)
async def read_video_review_list(
    response: Response,
    video_id: int,
    p: int = 1,
    ps: int = 20,
    db: AsyncSession = Depends(get_db),
):
    try:
        # 비디오 ID 파라메터 체크
        if not video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_VIDEO_ID"},
                detail=messages["INVALID_PARAM_VIDEO_ID"],
            )
        # 비디오 리뷰 목록 조회
        total, reviews = await queryset.read_video_review_list_with_rating(
            db, video_id, p, ps
        )
        # 비디오 리뷰 목록이 없을 경우
        if not reviews:
            response.headers["code"] = "REVIEW_NOT_FOUND"
        # Response Header Code
        response.headers["code"] = "REVIEW_READ_SUCC"
        # 리뷰 목록 생성
        return_reviews = [
            VideoReviewWithRating(
                id=review[0].id,
                video_id=review[0].video_id,
                user_id=review[0].user_id,
                user_nickname=review[0].user_nickname,
                user_profile_image=review[0].user_profile_image,
                title=review[0].title,
                content=review[0].content,
                like_count=review[0].like_count,
                is_spoiler=review[0].is_spoiler,
                created_at=review[0].created_at,
                updated_at=review[0].updated_at,
                rating=review[1],
            )
            for review in reviews
        ]
        # 비디오 리뷰 목록 반환
        return ResVideoReviews(
            total=total, count=len(reviews), page=1, data=return_reviews
        )
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
        # 비디오 ID 파라메터 체크
        if not video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_VIDEO_ID"},
                detail=messages["INVALID_PARAM_VIDEO_ID"],
            )
        # 리뷰 ID 파라메터 체크
        if not review_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_REVIEW_ID"},
                detail=messages["INVALID_PARAM_REVIEW_ID"],
            )
        # 리뷰 조회
        get_review = await queryset.read_video_review(db, review_id)
        if not get_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "REVIEW_NOT_FOUND"},
                detail=messages["REVIEW_NOT_FOUND"],
            )
        # 비디오 ID와 리뷰 비디오 ID 일치 여부 체크
        if video_id != get_review.video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "REVIEW_NOT_MATCH"},
                detail=messages["REVIEW_NOT_MATCH"],
            )
        # 회원 ID와 리뷰 회원 ID 일치 여부 체크
        if auth_user["id"] != get_review.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"code": "USER_NOT_MATCH"},
                detail=messages["USER_NOT_MATCH"],
            )
        # 리뷰 수정
        review = await queryset.update_video_review(db, review_id, req_review.dict())
        # 리뷰 수정 실패
        if not review:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                headers={"code": "REVIEW_UPDATE_FAIL"},
                detail=messages["REVIEW_UPDATE_FAIL"],
            )
        # Response Header Code
        response.headers["code"] = "REVIEW_UPDATE_SUCC"
        return
    except Exception as e:
        print(e)
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
        # 비디오 ID 파라메터 체크
        if not video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_VIDEO_ID"},
                detail=messages["INVALID_PARAM_VIDEO_ID"],
            )
        # 리뷰 ID 파라메터 체크
        if not review_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_REVIEW_ID"},
                detail=messages["INVALID_PARAM_REVIEW_ID"],
            )
        # 리뷰 조회
        get_review = await queryset.read_video_review(db, review_id)
        # 리뷰가 없을 경우
        if not get_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "REVIEW_NOT_FOUND"},
                detail=messages["REVIEW_NOT_FOUND"],
            )
        # 비디오 ID와 리뷰 비디오 ID 일치 여부 체크
        if video_id != get_review.video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "REVIEW_NOT_MATCH"},
                detail=messages["REVIEW_NOT_MATCH"],
            )
        # 회원 ID와 리뷰 회원 ID 일치 여부 체크
        if auth_user["id"] != get_review.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"code": "USER_NOT_MATCH"},
                detail=messages["USER_NOT_MATCH"],
            )
        # 리뷰 삭제
        review = await queryset.delete_video_review(db, review_id)
        # 리뷰 삭제 실패
        if not review:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                headers={"code": "REVIEW_DELETE_FAIL"},
                detail=messages["REVIEW_DELETE_FAIL"],
            )
        # 비디오 리뷰 수량 업데이트
        update = await queryset.update_video_review_count(db, video_id)
        if not update:
            response.headers["code"] = "REVIEW_COUNT_UPDATE_FAIL"
        # Response Header Code
        response.headers["code"] = "REVIEW_DELETE_SUCC"
        return
    except Exception as e:
        raise e


@router.post(
    "/videos/{video_id}/reviews/{review_id}/like",
    tags=[tags_review],
    status_code=status.HTTP_200_OK,
    response_model=ResData,
)
async def toggle_video_review_like(
    request: Request,
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
        is_review = await queryset.toggle_video_review_like(
            db, review_id, auth_user["id"]
        )
        is_review_count = await queryset.update_video_review_like_count(db, review_id)
        response.headers["code"] = "REVIEW_LIKE_UPDATE_SUCC"
        return ResData(data={"is_like": is_review, "like_count": is_review_count})
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


@router.post(
    "/videos/{video_id}/ratings",
    tags=[tags_rating],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def create_video_rating(
    response: Response,
    video_id: int,
    rating: int,
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
        # 평점 파라메터 체크
        if not rating or rating < 0 or rating > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "INVALID_PARAM_RATING"},
                detail=messages["INVALID_PARAM_RATING"],
            )
        # 비디오 조회
        get_video = await queryset.read_video(db, video_id=video_id)
        # 비디오가 없을 경우
        if not get_video:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                headers={"code": "VIDEO_NOT_FOUND"},
                detail=messages["VIDEO_NOT_FOUND"],
            )
        # 회원이 작성한 평점 조회
        get_rating = await queryset.read_video_rating_by_user(
            db, video_id, auth_user["id"]
        )
        if get_rating:
            # 삭제
            if rating == 0 or get_rating.rating == rating:
                # 삭제
                del_rating = await queryset.delete_video_rating(
                    db, video_id, auth_user["id"]
                )
                # 삭제 실패
                if not del_rating:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        headers={"code": "RATING_DELETE_FAIL"},
                        detail=messages["RATING_DELETE_FAIL"],
                    )
                # Response Header Code
                response.headers["code"] = "RATING_DELETE_SUCC"
            # 업데이트
            elif 0 < rating != get_rating.rating:
                # 업데이트
                upt_rating = await queryset.update_video_rating(
                    db, video_id, auth_user["id"], rating
                )
                # 업데이트 실패
                if not upt_rating:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        headers={"code": "RATING_UPDATE_FAIL"},
                        detail=messages["RATING_UPDATE_FAIL"],
                    )
                # Response Header Code
                response.headers["code"] = "RATING_UPDATE_SUCC"
        else:
            # 평점이 없는 경우
            if rating == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    headers={"code": "RATING_DOES_NOT_EXIST"},
                    detail=messages["RATING_DOES_NOT_EXIST"],
                )
            # 생성
            elif rating > 0 and not get_rating:
                # 생성
                cre_rating = await queryset.create_video_rating(
                    db, video_id, auth_user["id"], rating
                )
                # 생성 실패
                if not cre_rating:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        headers={"code": "RATING_CREATE_FAIL"},
                        detail=messages["RATING_CREATE_FAIL"],
                    )
                # Response Header Code
                response.headers["code"] = "RATING_CREATE_SUCC"
        return
    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )
