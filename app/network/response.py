from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.config.variables import messages

status_success = [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]
status_fail = [400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 421, 422, 423, 424, 425, 426, 428, 429, 431, 451, 500, 501, 502, 503, 504, 505, 506, 507, 508, 510, 511]


def json_response(status: int, code: str, data: dict | list | None = None):
    headers = dict()
    headers["code"] = code
    try:
        if status in status_success:
            content = dict()
            content["message"] = messages[code]

            if data:
                content_data = data
                if type(content_data) is not dict:
                    content_data = data
                content["data"] = content_data

            return JSONResponse(
                status_code=status,
                headers=headers,
                content=content
            )
        elif status in status_fail:
            raise HTTPException(
                status_code=status,
                headers=headers,
                detail=messages[code]
            )

        else:
            raise HTTPException(
                status_code=500,
                headers=headers,
                detail=messages[code]
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            headers=headers,
            detail=messages["EXCEPTION"]
        )









