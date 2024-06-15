import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Settings:
    # Default
    DEBUG: bool = os.getenv('DEBUG')
    APP_NAME: str = os.getenv('APP_NAME')
    BASE_DIR: str = BASE_DIR
    TIME_ZONE = ZoneInfo(os.getenv('TIME_ZONE'))
    DOCS_USER: bool = os.getenv('DOCS_USER')
    DOCS_PASSWORD: str = os.getenv('DOCS_PASSWORD')

    # Upload
    FILE_DIR = os.path.join(BASE_DIR, "static/uploads/")
    FILE_DIR_TEMP = os.path.join(FILE_DIR, "temp/")
    FILE_UPLOAD_TYPE_ALLOWED = [
        "image/jpeg",
        "image/jpg",
        "image/webp",
        "image/png",
        "image/gif",
        "image/bmp",
    ]

    # Security
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ALGORITHM: str = os.getenv('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_TIME: int = os.getenv('ACCESS_TOKEN_EXPIRE_TIME')
    REFRESH_TOKEN_EXPIRE_TIME: int = os.getenv('REFRESH_TOKEN_EXPIRE_TIME')

    # User
    # 10: email, 11: google, 12: facebook, 13: kakao, 14: naver, 15: apple
    USER_TYPE_ALLOW: list = ["10", "11", "12", "13", "14", "15"]
    USER_EMAIL_ALLOW_SPACE: bool = False
    USER_EMAIL_LENGTH_MIN: int = 5
    USER_EMAIL_LENGTH_MAX: int = 50
    USER_NICKNAME_ALLOW_SPACE: bool = False
    USER_NICKNAME_LENGTH_MIN: int = 2
    USER_NICKNAME_LENGTH_MAX: int = 20
    USER_PASSWORD_INCLUDE_SPACE: bool = False
    USER_PASSWORD_INCLUDE_WORD: bool = True
    USER_PASSWORD_INCLUDE_NUMBER: bool = True
    USER_PASSWORD_INCLUDE_SIMBOL: bool = True
    USER_PASSWORD_INCLUDE_UPPER: bool = False
    USER_PASSWORD_LENGTH_MIN: int = 8
    USER_PASSWORD_LENGTH_MAX: int = 22

    # Database
    DB_DRIVER: str = os.getenv('DB_DRIVER')
    DB_HOST: str = os.getenv('DB_HOST')
    DB_PORT: str = os.getenv('DB_PORT')
    DB_NAME: str = os.getenv('DB_NAME')
    DB_USER_NAME: str = os.getenv('DB_USER_NAME')
    DB_USER_PASSWORD: str = os.getenv('DB_USER_PASSWORD')

    # AWS S3
    AWS_S3_BUCKET_REGION: str = os.getenv('AWS_S3_BUCKET_REGION')
    AWS_S3_BUCKET_NAME: str = os.getenv('AWS_S3_BUCKET_NAME')
    AWS_S3_ACCESS_KEY_ID: str = os.getenv('AWS_S3_ACCESS_KEY_ID')
    AWS_S3_SECRET_ACCESS_KEY: str = os.getenv('AWS_S3_SECRET_ACCESS_KEY')

    AWS_S3_PATH_USER_PROFILE_IMAGE = "users/profile/images/"

    # CORS origins
    CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:8080",
    ]


settings = Settings()

    