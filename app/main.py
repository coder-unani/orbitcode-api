from fastapi import FastAPI
from fastapi_pagination import add_pagination

from fastapi.middleware.cors import CORSMiddleware

from app.routes import contents
from app.config.settings import settings

def create_app():

    # FastAPI initialize
    app = FastAPI()

    # Middleware 정의
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True, # cross-origin request에서 cookie를 허용
        allow_methods=["*"], # 모든 HTTP 메서드 허용
        allow_headers=["*"], # 모든 HTTP 헤더 허용
    )

    # Router 정의
    app.include_router(contents.router, prefix="/contents")

    # App 반환
    return app

app = create_app()
# Pagination
add_pagination(app)