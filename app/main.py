import os
from fastapi import FastAPI, Depends, Response
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from app.config.settings import settings
from app.middleware.logging import LoggingMiddleware
from app.security.verifier import verify_access_docs
from app.utils.logger import Logger
from app.routes.v1 import (
    defaults as defaults_v1,
    users as users_v1,
    videos as videos_v1,
    validation as validation_v1,
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
        # allow_origins=settings.CORS_ORIGINS,
        allow_origins=["*"],  # 모든 Origin 허용
        allow_credentials=True,  # cross-origin request에서 cookie를 허용
        # allow_methods=["*"],  # 모든 HTTP 메서드 허용
        # allow_headers=["*"],  # 모든 HTTP 헤더 허용
        allow_methods=["GET", "POST", "PUT", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        expose_headers=["ACCESS-ORIGIN-EXPOSED-HEADERS"],  # Custom Header 허용
    )

    # Logging Middleware 정의
    if not settings.DEBUG == "True":
        api.add_middleware(LoggingMiddleware, logger=Logger(log_dir=settings.LOG_DIR))

    # Router 정의
    api.include_router(defaults_v1.router, prefix="/v1")
    api.include_router(users_v1.router, prefix="/v1")
    api.include_router(videos_v1.router, prefix="/v1/contents")
    api.include_router(validation_v1.router, prefix="/v1/validation")

    return api


# FastAPI instance
app: FastAPI = create_api()

# Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Robots.txt
@app.get("/robots.txt", include_in_schema=False, response_class=PlainTextResponse)
def robots():
    return Response(content="User-agent: *\nDisallow: /", media_type="text/plain")


# API Documentation
@app.get(
    "/api/docs", include_in_schema=False, dependencies=[Depends(verify_access_docs)]
)
def get_documentation():
    with open(os.path.join("static", "swagger_ui.html")) as f:
        html_content = f.read()
    return Response(content=html_content, media_type="text/html")


# OpenAPI Schema
@app.get(
    "/api/openapi.json",
    include_in_schema=False,
    dependencies=[Depends(verify_access_docs)],
)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Orbitcode API Documentation",
        version="0.1.0",
        description="안녕하세요 Orbitcode API 문서입니다. Reviewniverse APIs를 제공하고 있습니다.",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "/static/assets/reviewniverse-logo-1.png",
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Main
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
