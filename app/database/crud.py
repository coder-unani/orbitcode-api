from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import schemas, models

def get_videos(db: Session, is_delete: bool|None = None):
    videos = []
    if is_delete is None:
        videos = db.query(models.ContentsVideo).all()
    else:
        videos = db.query(models.ContentsVideo).filter(
            models.ContentsVideo.is_delete == is_delete,
            models.ContentsVideoWatch.is_delete == is_delete,
            models.ContentsVideoGenre.is_delete == is_delete,
            models.ContentsVideoStaff.is_delete == is_delete,
            models.ContentsVideoAttach.is_delete == is_delete
        ).all()
    
    return videos

def get_video_by_id(db: Session, video_id: int, is_delete: bool|None = None):

    if is_delete is None:
        video = db.query(models.ContentsVideo).filter(models.ContentsVideo.id == video_id).first()
    else:
        video = db.query(models.ContentsVideo).filter(
            models.ContentsVideo.id == video_id, 
            models.ContentsVideo.is_delete == is_delete,
            models.ContentsVideoWatch.is_delete == is_delete,
            models.ContentsVideoGenre.is_delete == is_delete,
            models.ContentsVideoStaff.is_delete == is_delete,
            models.ContentsVideoAttach.is_delete == is_delete
        ).first()
        
    return video