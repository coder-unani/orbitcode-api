from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import ContentsVideo

def get_videos(db: Session, page: int, is_delete: bool|None = None, is_confirm: bool|None = None, keyword: str|None = None):
    unit_per_page = 20
    offset = (page - 1) * unit_per_page

    videos = db.query(ContentsVideo)
    if is_delete is not None:
        videos = videos.filter(ContentsVideo.is_delete == is_delete)
    if is_confirm is not None:
        videos = videos.filter(ContentsVideo.is_confirm == is_confirm)
    if keyword is not None:
        videos = videos.filter(ContentsVideo.title.contains(keyword, autoescape=True))
    else:
        videos = db.query(ContentsVideo)

    total = videos.count()
    videos = videos.offset(offset).limit(unit_per_page).all()

    return total, videos

def get_video_by_id(db: Session, video_id: int):

    video = db.query(ContentsVideo).filter(ContentsVideo.id == video_id).first()
    
    return video