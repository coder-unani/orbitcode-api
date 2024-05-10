from datetime import datetime

from pydantic import BaseModel, Field

class ContentsVideoWatch(BaseModel):
    watch_type: str
    watch_url: str
    sort: int
    # is_delete: bool
    # created_at: datetime
    # updated_at: datetime

    class Config:
        from_attributes = True

class ContentsVideoGenre(BaseModel):
    genre: str
    sort: int
    # is_delete: bool
    # created_at: datetime
    # updated_at: datetime

    class Config:
        from_attributes = True

class ContentsVideoStaff(BaseModel):
    staff_type: str
    staff_name: str
    sort: int
    # is_delete: bool
    # created_at: datetime
    # updated_at: datetime

    class Config:
        from_attributes = True

class ContentsVideoAttach(BaseModel):
    attach_type: str
    attach_url: str
    sort: int
    # is_delete: bool
    # created_at: datetime
    # updated_at: datetime

    class Config:
        from_attributes = True

class ContentsVideo(BaseModel):
    id: int = Field(0, title="VIDEO ID")
    title: str
    synopsis: str
    release: str
    notice_age: str
    runtime: str
    platform_code: str
    platform_id: str
    is_confirm: bool
    is_delete: bool
    created_at: datetime
    updated_at: datetime

    watchs: list[ContentsVideoWatch] = []
    genres: list[ContentsVideoGenre] = []
    staffs: list[ContentsVideoStaff] = []
    attachs: list[ContentsVideoAttach] = []

    class Config:
        from_attributes = True


class ResponseContentsVideos(BaseModel):
    status: str = "success"
    message: str = ""
    data: list[ContentsVideo] = []
    

class ResponseContentsVideo(BaseModel):
    status: str = "success"
    message: str = ""
    data: ContentsVideo = None