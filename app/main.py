from fastapi import FastAPI
from fastapi import APIRouter, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.routes import users, contents
from app.config.settings import settings
from app.security.verifier import verify_access_token_user


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

    router = APIRouter()

    # Router 정의
    api.include_router(users.router, prefix="/users")
    api.include_router(contents.router, prefix="/contents", dependencies=[Depends(verify_access_token_user)])

    return api


app: FastAPI = create_api()
