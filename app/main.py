import secrets
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.security.verifier import verify_access_docs
from app.config.settings import settings
from app.routes.v1 import (
    defaults as defaults_v1,
    users as users_v1,
    contents as contents_v1,
    reviews as reviews_v1
)


SWAGGER_HEADERS = {
    "title": settings.APP_NAME,
    "version": "0.1.0",
    "description": "ORBITCODE API<br/><a href='https://www.orbitcode.kr' target='_blank'>www.orbitcode.kr</a>"
}


# FastAPI initialize
def create_api() -> FastAPI:
    api = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
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


@app.get("/api/docs", include_in_schema=False, dependencies=[Depends(verify_access_docs)])
def get_documentation():
    return get_swagger_ui_html(openapi_url="/api/openapi.json", title="docs")


@app.get("/api/openapi.json", include_in_schema=False, dependencies=[Depends(verify_access_docs)])
async def openapi():
    return get_openapi(
        title=SWAGGER_HEADERS['title'],
        version=SWAGGER_HEADERS['version'],
        routes=app.routes)
