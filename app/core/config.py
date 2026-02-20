from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILES = (".env.example", ".env", ".env.local")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./app.db"
    test_database_url: str = ""
    use_external_test_db: bool = False
    jwt_secret: str = "change-me"
    paystack_secret_key: str = ""
    paystack_public_key: str = ""
    paystack_webhook_token: str = ""
    telegram_webhook_token: str = ""
    whatsapp_verify_token: str = ""
    whatsapp_app_secret: str = ""
    gemini_api_key: str = ""
    media_dir: str = "media"
    cloudflare_account_id: str = ""
    r2_bucket_name: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_endpoint_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
