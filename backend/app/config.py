from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = Field(default=3306, ge=1, le=65535)
    db_name: str = "temperature_db"
    db_user: str = "admin"
    db_password: str = ""
    serial_port: str = ""
    serial_baud_rate: int = Field(default=9600, ge=300, le=115200)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

