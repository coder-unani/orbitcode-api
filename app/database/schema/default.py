from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class ResponseModel(BaseModel):
    status: str = "success"
    code: str = ""
    message: str = ""


class ResponseDataModel(ResponseModel):
    data: dict | None = None








