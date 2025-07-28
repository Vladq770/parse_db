import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Класс настроек."""

    BASE_URL: str = os.getenv("BASE_URL")
    PASSWORD: str = os.getenv("PASSWORD")
    LOGIN: str = os.getenv("LOGIN")

    DB_NAME: str = os.getenv("DB_NAME")
    TABLE_NAME: str = os.getenv("TABLE_NAME")

    BASE_DELAY: float = os.getenv("BASE_DELAY", default=1.0)
    DELAY_MULTIPLIER: float = os.getenv("DELAY_MULTIPLIER", default=1.0)


settings = Settings()
