from fastapi import FastAPI
from fastapi import APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.routes.v1 import (
    defaults as defaults_v1,
    users as users_v1,
    contents as contents_v1,
    reviews as reviews_v1
)
from app.config.settings import settings


SWAGGER_HEADERS = {
    "title": settings.APP_NAME,
    "version": "0.1.0",
    "description": "ORBITCODE API<br/><a href='https://www.orbitcode.kr' target='_blank'>www.orbitcode.kr</a>"
}


# FastAPI initialize
def create_api() -> FastAPI:
    api = FastAPI(
        swagger_ui_parameters={
            "deepLinking": "true",
            "displayRequestDuration": "true",
            "docExpansion": "none",
            "operationsSorter": "alpha",
            "filter": True,
            "tagsSorter": "alpha",
            "syntaxHighlight.theme": "tomorrow-night",
        },
        **SWAGGER_HEADERS
    )

    # Middleware 정의
    api.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,  # cross-origin request에서 cookie를 허용
        allow_methods=["*"],  # 모든 HTTP 메서드 허용
        allow_headers=["*"],  # 모든 HTTP 헤더 허용
    )

    # Router 정의
    api.include_router(defaults_v1.router, prefix="/v1")
    api.include_router(users_v1.router, prefix="/v1")
    api.include_router(contents_v1.router, prefix="/v1")
    # api.include_router(review_v1.router, prefix="/v1")

    return api


app: FastAPI = create_api()
