import os
from dotenv import load_dotenv

ENV_NAME = "development"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(BASE_DIR, f".env.{ENV_NAME}"))

class Settings:
    # Default
    APP_NAME: str = "ORBITCODE APIs"
    BASE_DIR: str = BASE_DIR

    # Database
    DB_DRIVER: str = os.getenv('DB_DRIVER')
    DB_HOST: str = os.getenv('DB_HOST')
    DB_PORT: str = os.getenv('DB_PORT')
    DB_NAME: str = os.getenv('DB_NAME')
    DB_USER_NAME: str = os.getenv('DB_USER_NAME')
    DB_USER_PASSWORD: str = os.getenv('DB_USER_PASSWORD')

    # AWS S3
    AWS_BUCKET_REGION: str = os.getenv('AWS_BUCKET_REGION')
    AWS_BUCKET_NAME: str = os.getenv('AWS_BUCKET_NAME')
    AWS_ACCESS_KEY_ID: str = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY: str = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    # CORS origins
    CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
settings = Settings()

    