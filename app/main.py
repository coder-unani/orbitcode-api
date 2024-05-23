from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import contents
from app.config.settings import settings


# FastAPI initialize
def create_api() -> FastAPI:
    api = FastAPI()

    # Middleware 정의
    api.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,  # cross-origin request에서 cookie를 허용
        allow_methods=["*"],  # 모든 HTTP 메서드 허용
        allow_headers=["*"],  # 모든 HTTP 헤더 허용
    )

    # Router 정의
    api.include_router(contents.router, prefix="/contents")

    return api


app: FastAPI = create_api()
