from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.routes import contents

def create_app():

    # FastAPI initialize
    app = FastAPI()

    # Middleware 정의

    # Router 정의
    app.include_router(contents.router, prefix="/contents")

    # App 반환
    return app

app = create_app()
# Pagination
add_pagination(app)