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
    reviews as reviews_v1,
    admins as admins_v1
)


description = """
오르빗코드(Orbitcode) API 서버입니다.

## users
- **/users/create**: 회원가입
- **/users/login**: 로그인
- **/users/me**: 내 정보 조회
- **/users/me/update**: 내 정보 수정

## contents
"""
SWAGGER_HEADERS = {
    "title": settings.APP_NAME,
    "version": "0.1.0",
    "description": description,
    "terms_of_service": "http://example.com/terms/",
    "contact": {
        "name": "ORBITCODE",
        "url": "https://www.orbitcode.kr",
        "email": "info@orbitcode.kr",
    },
    "license": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    "swagger_ui_parameters": {
            "deepLinking": "true",
            "displayRequestDuration": "true",
            "docExpansion": "none",
            "operationsSorter": "alpha",
            "filter": True,
            "tagsSorter": "alpha",
            "syntaxHighlight.theme": "tomorrow-night",
    },
    "openapi_tags": [
        {
            "name": "users",
            "description": "Operations with users. The **login** logic is also here.",
        },
        {
            "name": "contents",
            "description": "Operations with contents. The **videos** logic is also here.",
        }
    ],
}


# FastAPI initialize
def create_api() -> FastAPI:
    api = FastAPI(
        description=description,
        title=SWAGGER_HEADERS['title'],
        docs_url=None,
        redoc_url=None,
        openapi_url=None,

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
    api.include_router(admins_v1.router, prefix="/v1/admins")

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


# 메모리 누수 테스트
# 테스트 필요한 곳에 @profile 데코레이터 추가
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# python3 -m memory_profiler app/main.py
