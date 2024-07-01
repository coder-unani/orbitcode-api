from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import insert, update, delete
from sqlalchemy.orm import aliased

from app.config.variables import messages
from app.database.model.videos import (
    Video,
    Genre,
    Actor,
    Staff,
    VideoViewLog,
    VideoLike,
    VideoReview,
    VideoReviewLike,
    VideoRating,
)


async def search_video_list(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    video_code: str | None = None,
    keyword: str | None = None,
    video_id: int | None = None,
    actor_id: int | None = None,
    staff_id: int | None = None,
    genre_id: int | None = None,
    is_delete: bool = False,
    is_confirm: bool = True,
    order_by: str | None = None,
):
    unit_per_page = page_size
    offset = (page - 1) * unit_per_page

    try:
        stmt = select(Video)
        if video_id is not None:
            stmt = stmt.filter_by(id=video_id)
        if video_code is not None:
            stmt = stmt.filter_by(code=video_code)
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
    is_delete: bool = False,
    is_confirm: bool = True,
):
    try:
        stmt = select(Video)
        # Filter
        if video_id is not None:
            stmt = stmt.filter_by(id=video_id)
        if is_delete is not None:
            stmt = stmt.filter_by(is_delete=is_delete)
        if is_confirm is not None:
            stmt = stmt.filter_by(is_confirm=is_confirm)
        video: Video = await db.scalar(stmt)
        return video
    except Exception as e:
        print(e)
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
                stmt_view_log = insert(VideoViewLog).values(
                    video_id=video_id, client_ip=client_ip
                )
            # VideoViewLog Insert
            await db.execute(stmt_view_log)
        # 같은 Video ID의 조회수 Count
        view_count = await db.scalar(
            select(func.count()).where(VideoViewLog.video_id == video_id)
        )
        # Video 조회수 Update
        stmt_update = (
            update(Video).where(Video.id == video_id).values(view_count=view_count)
        )
        await db.execute(stmt_update)
        await db.commit()
        # 조회수 반환
        return view_count
    except Exception as e:
        print(e)
        # Exception 발생 시 Rollback
        await db.rollback()
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
        stmt = select(VideoReview).filter_by(video_id=video_id, is_block=False)
        if is_private is not None:
            stmt = stmt.filter_by(is_private=is_private)
        if is_block is not None:
            stmt = stmt.filter_by(is_block=is_block)
        stmt.order_by(VideoReview.created_at.desc())
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


async def read_video_review_list_with_rating(
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
        video_review_alias = aliased(VideoReview)
        video_rating_alias = aliased(VideoRating)
        stmt = (
            select(video_review_alias, video_rating_alias.rating)
            .outerjoin(
                video_rating_alias,
                (video_review_alias.video_id == video_rating_alias.video_id)
                & (video_review_alias.user_id == video_rating_alias.user_id),
            )
            .where(video_review_alias.video_id == video_id)
        )
        if is_private is not None:
            stmt = stmt.where(video_review_alias.is_private == is_private)
        if is_block is not None:
            stmt = stmt.where(video_review_alias.is_block == is_block)
        stmt = stmt.order_by(desc(video_review_alias.created_at))
        # Total Count
        total = await db.scalar(select(func.count()).select_from(stmt.alias()))
        # Review List
        result = await db.execute(stmt.offset(offset).limit(unit_per_page))
        reviews = result.all()
        # 결과 반환
        return total, reviews
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def read_video_review(db: AsyncSession, review_id: int):
    try:
        stmt = select(VideoReview).filter_by(
            id=review_id, is_block=False, is_private=False
        )
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
        stmt = select(VideoReview).filter_by(
            video_id=video_id, user_id=user_id, is_block=False, is_private=False
        )
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


async def read_video_rating_by_user(db: AsyncSession, video_id: int, user_id: int):
    try:
        stmt = select(VideoRating).filter_by(video_id=video_id, user_id=user_id)
        rating = await db.scalar(stmt)
        return rating
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def create_video_rating(
    db: AsyncSession, video_id: int, user_id: int, rating: int
):
    try:
        # 리뷰 Insert
        stmt = insert(VideoRating).values(
            video_id=video_id, user_id=user_id, rating=rating
        )
        await db.execute(stmt)
        await db.commit()
        return True
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def update_video_rating(
    db: AsyncSession, video_id: int, user_id: int, rating: int
):
    try:
        # 리뷰 Update
        stmt = (
            update(VideoRating)
            .where(VideoRating.video_id == video_id, VideoRating.user_id == user_id)
            .values(rating=rating)
        )
        await db.execute(stmt)
        await db.commit()
        return True
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def delete_video_rating(db: AsyncSession, video_id: int, user_id: int):
    try:
        # 리뷰 Delete
        stmt = delete(VideoRating).where(
            VideoRating.video_id == video_id, VideoRating.user_id == user_id
        )
        await db.execute(stmt)
        await db.commit()
        return True
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
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


async def toggle_video_review_like(db: AsyncSession, review_id: int, user_id: int):
    try:
        print("review_id", review_id)
        print("user_id", user_id)
        is_review_like = await db.scalar(
            select(VideoReviewLike.is_like).filter_by(review_id=review_id)
        )
        if is_review_like is None:
            is_review_like = True
            stmt = insert(VideoReviewLike).values(
                review_id=review_id, user_id=user_id, is_like=is_review_like
            )
        else:
            is_review_like = not is_review_like
            stmt = (
                update(VideoReviewLike)
                .where(
                    VideoReviewLike.review_id == review_id,
                    VideoReviewLike.user_id == user_id,
                )
                .values(is_like=is_review_like)
            )
        # 업데이트
        await db.execute(stmt)
        await db.commit()
        return is_review_like
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def update_video_view_count(db: AsyncSession, video_id: int):
    pass


async def update_video_review_count(db: AsyncSession, video_id: int):
    try:
        # 비디오 리뷰 카운팅
        review_stmt = select(VideoReview).filter_by(video_id=video_id)
        review_count = await db.scalar(select(func.count()).select_from(review_stmt))
        # 비디오 리뷰 카운팅 업데이트
        update_stmt = (
            update(Video)
            .where(Video.id == video_id)
            .values(review_count=review_count)
            .returning(Video.review_count)
        )
        await db.execute(update_stmt)
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


async def update_video_review_like_count(db: AsyncSession, review_id: int):
    try:
        # 리뷰 좋아요 카운팅
        like_stmt = select(VideoReviewLike).filter_by(review_id=review_id, is_like=True)
        like_count = await db.scalar(select(func.count()).select_from(like_stmt))
        print("like_count", like_count)
        # 리뷰 좋아요 카운팅 업데이트
        update_stmt = (
            update(VideoReview)
            .where(VideoReview.id == review_id)
            .values(like_count=like_count)
            .returning(VideoReview.like_count)
        )
        await db.execute(update_stmt)
        await db.commit()
        return like_count
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def update_video_like_count(db: AsyncSession, video_id: int):
    try:
        # 비디오 좋아요 카운팅
        select_stmt = select(VideoLike).filter_by(video_id=video_id, is_like=True)
        like_count = await db.scalar(select(func.count()).select_from(select_stmt))
        # 비디오 좋아요 카운팅 업데이트
        update_stmt = (
            update(Video).where(Video.id == video_id).values(like_count=like_count)
        )
        # 업데이트 쿼리 실행
        await db.execute(update_stmt)
        await db.commit()
        # 업데이트된 좋아요 카운팅 반환
        return like_count
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def read_video_my_is_like(db: AsyncSession, video_id: int, user_id: int):
    try:
        print("read_video_my_is_like start")
        is_like = await db.scalar(
            select(VideoLike.is_like).filter_by(
                video_id=video_id, user_id=user_id, is_like=True
            )
        )
        print("read_video_my_is_like end")
        return is_like
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def read_video_my_review(db: AsyncSession, video_id: int, user_id: int):
    try:
        review = await db.scalar(
            select(VideoReview).filter_by(
                video_id=video_id, user_id=user_id, is_block=False
            )
        )
        return review
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def read_video_my_review_like(db: AsyncSession, video_id: int, user_id: int):
    try:
        print("read_video_my_review_like start")

        # Alias for the VideoReview table to be used in join
        video_review_alias = aliased(VideoReview)

        # Select review IDs for the given video and user
        video_review_ids = await db.execute(
            select(video_review_alias.id).filter_by(video_id=video_id, user_id=user_id)
        )
        video_review_ids = video_review_ids.scalars().all()

        if not video_review_ids:
            return []

        # Select review_like_ids where the review is liked by the user
        review_like_ids = await db.execute(
            select(VideoReviewLike.review_id)
            .join(
                video_review_alias, VideoReviewLike.review_id == video_review_alias.id
            )
            .where(
                video_review_alias.id.in_(video_review_ids),
                VideoReviewLike.user_id == user_id,
                VideoReviewLike.is_like.is_(True),
            )
        )
        result = review_like_ids.scalars().all()
        print("read_video_my_review_like end")
        return result
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def read_video_my_rating(db: AsyncSession, video_id: int, user_id: int):
    try:
        rating = await db.scalar(
            select(VideoRating.rating).filter_by(video_id=video_id, user_id=user_id)
        )
        return rating
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def read_genre(db: AsyncSession, genre_id: int):
    try:
        stmt = select(Genre).filter_by(id=genre_id)
        genre = await db.scalar(stmt)
        return genre
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def read_actor(db: AsyncSession, actor_id: int):
    try:
        stmt = select(Actor).filter_by(id=actor_id)
        actor = await db.scalar(stmt)
        return actor
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )


async def read_staff(db: AsyncSession, staff_id: int):
    try:
        stmt = select(Staff).filter_by(id=staff_id)
        staff = await db.scalar(stmt)
        return staff
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"code": "EXCEPTION"},
            detail=messages["EXCEPTION"],
        )
