import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import computed_field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY")

    SERVER_HOST: str = os.getenv("SERVER_HOST")
    SERVER_PORT: int = os.getenv("SERVER_PORT")

    PROJECT_NAME: str = os.getenv("PROJECT_NAME")

    # Email Config
    SMTP_TLS: bool = os.getenv("SMTP_TLS")
    SMTP_SSL: bool = False
    SMTP_PORT: int = os.getenv("SMTP_PORT")
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAILS_FROM_EMAIL: Optional[str] = os.getenv("EMAILS_FROM_EMAIL")
    EMAILS_FROM_NAME: Optional[str] = os.getenv("EMAILS_FROM_NAME")
    EMAIL_TO: Optional[str] = os.getenv("EMAIL_TO")

    # LAZADA Config
    LAZADA_ROOT_URL: str = os.getenv("LAZADA_ROOT_URL")
    LAZADA_APP_KEY: str = os.getenv("LAZADA_APP_KEY")
    LAZADA_APP_SECRET: str = os.getenv("LAZADA_APP_SECRET")

    @computed_field
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    class Config:
        case_sensitive = True


settings = Settings()
