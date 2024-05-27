from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class AccessLog(BaseModel):
    id: int
    status: int
    path: str
    ip: str
    user_id: int
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class ResponseModel(BaseModel):
    status: str = "success"
    code: str = ""
    message: str = ""






