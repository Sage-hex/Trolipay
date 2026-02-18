from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local", ".env.example"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./app.db"
    test_database_url: str = ""
    jwt_secret: str = "change-me"
    paystack_secret_key: str = ""
    paystack_webhook_token: str = ""
    telegram_webhook_token: str = ""
    whatsapp_verify_token: str = ""
    whatsapp_app_secret: str = ""
    media_dir: str = "media"


@lru_cache
def get_settings() -> Settings:
    return Settings()
