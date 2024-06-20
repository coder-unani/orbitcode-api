from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import insert, update, delete

from app.config.variables import messages
from app.database.model.videos import Video, VideoViewLog, VideoLike, VideoReview


async def search_video_list(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    video_type: str | None = None,
    keyword: str | None = None,
    video_id: int | None = None,
    actor_id: int | None = None,
    staff_id: int | None = None,
    genre_id: int | None = None,
    platform_id: str | None = None,
    is_delete: bool | None = None,
    is_confirm: bool | None = None,
    order_by: str | None = None,
):
    unit_per_page = page_size
    offset = (page - 1) * unit_per_page

    try:
        stmt = select(Video)
        if video_id is not None:
            stmt = stmt.filter_by(id=video_id)
        if video_type is not None:
            stmt = stmt.filter_by(type=video_type)
        if platform_id is not None:
            stmt = stmt.filter_by(platform_id=platform_id)
        if is_delete is not None:
            stmt = stmt.filter_by(is_delete=is_delete)
        if is_confirm is not None:
            stmt = stmt.filter_by(is_confirm=is_confirm)
        if keyword is not None:
            stmt = stmt.filter(Video.title.contains(keyword, autoescape=True))
        if actor_id is not None:
            stmt = stmt.join(Video.actor).filter_by(id=actor_id)
        if staff_id is not None:
            stmt = stmt.join(Video.staff).filter_by(id=staff_id)
        if genre_id is not None:
            stmt = stmt.join(Video.genre).filter_by(id=genre_id)
        if order_by is not None:
            if order_by == "view_desc":
                stmt = stmt.order_by(Video.view_count.desc())
            elif order_by == "view_asc":
                stmt = stmt.order_by(Video.view_count.asc())
            elif order_by == "like_desc":
                stmt = stmt.order_by(Video.like_count.desc())
            elif order_by == "like_asc":
                stmt = stmt.order_by(Video.like_count.asc())
            elif order_by == "new_desc":
                stmt = stmt.order_by(Video.created_at.desc())
            elif order_by == "new_desc":
                stmt = stmt.order_by(Video.created_at.asc())
            elif order_by == "updated_desc":
                stmt = stmt.order_by(Video.updated_at.desc())
            elif order_by == "updated_asc":
                stmt = stmt.order_by(Video.updated_at.asc())
            elif order_by == "title_desc":
                stmt = stmt.order_by(Video.title.desc())
            elif order_by == "title_asc":
                stmt = stmt.order_by(Video.title.asc())
            elif order_by == "rating_desc":
                stmt = stmt.order_by(Video.rating.desc())
            elif order_by == "rating_asc":
                stmt = stmt.order_by(Video.rating.asc())

        # Total count
        total = await db.scalar(select(func.count()).select_from(stmt))
        result = await db.execute(stmt.offset(offset).limit(unit_per_page))
        videos = result.scalars().all()

        return total, videos

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


async def read_video(
    db: AsyncSession,
    video_id: int = None,
    platform_id: str = None,
    is_delete: bool = False,
    is_confirm: bool = False,
):
    try:
        stmt = select(Video)
        # Filter
        if video_id is not None:
            stmt = stmt.filter_by(id=video_id)
        if platform_id is not None:
            stmt = stmt.filter_by(platform_id=platform_id)
        if is_delete is not None:
            stmt = stmt.filter_by(is_delete=is_delete)
        if is_confirm is not None:
            stmt = stmt.filter_by(is_confirm=is_confirm)
        video: Video = await db.scalar(stmt)
        return video
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def insert_video_view(
    db: AsyncSession,
    video_id: int,
    user_id: int | None = None,
    client_ip: str | None = None,
):
    today = datetime.today().date()
    try:
        # Video 조회수 중복 체크 (하루에 한 번)
        client_view_count = await db.scalar(
            select(func.count()).where(
                VideoViewLog.video_id == video_id,
                VideoViewLog.client_ip == client_ip,
                func.date(VideoViewLog.created_at) == today,
            )
        )
        # 중복 조회수가 없을 경우
        if client_view_count <= 0:
            # user_id가 있을 경우
            if user_id:
                stmt_view_log = insert(VideoViewLog).values(
                    video_id=video_id, user_id=user_id, client_ip=client_ip
                )
            # user_id가 없을 경우
            else:
                stmt_view_log = insert(VideoViewLog).values(video_id=video_id)
            # VideoViewLog Insert
            await db.execute(stmt_view_log)
        # 같은 Video ID의 조회수 Count
        view_count = await db.scalar(
            select(func.count()).where(VideoViewLog.video_id == video_id)
        )
        # Video 조회수 Update
        stmt_update = (
            update(Video)
            .where(Video.id == video_id)
            .values(view_count=view_count)
            .returning(Video.view_count)
        )
        await db.execute(stmt_update)
        await db.commit()
        # 조회수 반환
        return view_count
    except Exception as e:
        # Exception 발생 시 Rollback
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def toggle_video_like(db: AsyncSession, video_id: int, user_id: int):
    try:
        video = await db.scalar(select(Video).where(Video.id == video_id))
        video_title = video.title
        is_like = await db.scalar(
            select(VideoLike.is_like).filter_by(video_id=video_id, user_id=user_id)
        )
        if is_like is None:
            is_like = True
            stmt = insert(VideoLike).values(
                video_id=video_id,
                video_title=video_title,
                user_id=user_id,
                is_like=is_like,
            )
        else:
            is_like = not is_like
            stmt = (
                update(VideoLike)
                .where(VideoLike.video_id == video_id, VideoLike.user_id == user_id)
                .values(is_like=is_like)
            )
        await db.execute(stmt)
        await db.commit()
        return is_like
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def read_video_review_list(
    db: AsyncSession,
    video_id: int,
    page: int = 1,
    page_size: int = 20,
    is_private: bool = False,
    is_block: bool = False,
):
    # 페이징 변수
    unit_per_page = page_size
    offset = (page - 1) * unit_per_page
    try:
        # QuerySet 생성
        stmt = select(VideoReview).filter_by(video_id=video_id)
        if is_private is not None:
            stmt = stmt.filter_by(is_private=is_private)
        if is_block is not None:
            stmt = stmt.filter_by(is_block=is_block)
        # Total Count
        total = await db.scalar(select(func.count()).select_from(stmt))
        # Review List
        result = await db.execute(stmt.offset(offset).limit(unit_per_page))
        reviews = result.scalars().all()
        # 결과 반환
        return total, reviews
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def read_video_review(db: AsyncSession, review_id: int):
    try:
        stmt = select(VideoReview).filter_by(id=review_id)
        review: VideoReview = await db.scalar(stmt)
        return review
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def read_video_review_by_user(db: AsyncSession, video_id: int, user_id: int):
    try:
        stmt = select(VideoReview).filter_by(video_id=video_id, user_id=user_id)
        review: VideoReview = await db.scalar(stmt)
        return review
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def create_video_review(db: AsyncSession, req_review: dict):
    try:
        # 리뷰 Insert
        stmt = insert(VideoReview).values(**req_review)
        await db.execute(stmt)
        await db.commit()
        return True
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def update_video_review(db: AsyncSession, review_id: int, req_review: dict):
    try:
        # 리뷰 Update
        stmt = (
            update(VideoReview).where(VideoReview.id == review_id).values(**req_review)
        )
        await db.execute(stmt)
        await db.commit()
        return True
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def delete_video_review(db: AsyncSession, review_id: int):
    try:
        # 리뷰 Delete
        stmt = delete(VideoReview).where(VideoReview.id == review_id)
        await db.execute(stmt)
        await db.commit()
        return True
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )
