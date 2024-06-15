from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str


class ResData(BaseModel):
    data: dict | list | None = None


# class ResponseToken(ResponseData):
#     data: Token | None = None






