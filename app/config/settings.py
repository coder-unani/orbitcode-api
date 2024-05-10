import os
from dotenv import load_dotenv

ENV_NAME = "development"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("path")
print(os.path.join(BASE_DIR, f".env.{ENV_NAME}"))
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

settings = Settings()

    