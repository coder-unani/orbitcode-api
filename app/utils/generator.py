from app.config.variables import messages


def make_response(status: str, code: str, data: dict | list | None = None):
    response = {
        "status": messages[status],
        "code": code,
        "message": messages[code]
    }
    if data:
        response["data"] = data

    return response
