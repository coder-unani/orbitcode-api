import secrets
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.config.settings import settings
from app.middleware.logging import LoggingMiddleware
from app.security.verifier import verify_access_docs
from app.utils.logger import Logger
from app.routes.v1 import (
    defaults as defaults_v1,
    users as users_v1,
    videos as videos_v1,
    finds as finds_v1,
    reviews as reviews_v1
)


# FastAPI initialize
def create_api() -> FastAPI:
    api = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    # CORS Middleware 정의
    api.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,  # cross-origin request에서 cookie를 허용
        allow_methods=["*"],  # 모든 HTTP 메서드 허용
        allow_headers=["*"],  # 모든 HTTP 헤더 허용
    )
    # Logging Middleware 정의
    if not settings.DEBUG:
        api.add_middleware(LoggingMiddleware, logger=Logger())
    # Router 정의
    api.include_router(defaults_v1.router, prefix="/v1")
    api.include_router(users_v1.router, prefix="/v1")
    api.include_router(finds_v1.router, prefix="/v1/finds")
    api.include_router(videos_v1.router, prefix="/v1/contents")
    # api.include_router(review_v1.router, prefix="/v1")
    return api


app: FastAPI = create_api()


@app.get("/api/docs", include_in_schema=False, dependencies=[Depends(verify_access_docs)])
def get_documentation():
    return get_swagger_ui_html(openapi_url="/api/openapi.json", title="docs")


@app.get("/api/openapi.json", include_in_schema=False, dependencies=[Depends(verify_access_docs)])
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Orbitcode API Documentation",
        version="0.1.0",
        description="Orbitcode가 Reviewniverse API를 제공합니다.",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
