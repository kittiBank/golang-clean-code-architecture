from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from GOAPP_* environment variables or .env."""

    model_config = SettingsConfigDict(
        env_prefix="GOAPP_",
        env_file=".env",
        extra="ignore",  # .env also carries MongoDB vars we don't use yet
    )

    host: str = "127.0.0.1"
    port: int = 3000
    name: str = "GOLANG FIRST API APP"
    version: str = "0.0.1"

    postgres_db_name: str = "postgres"
    postgres_db_user: str = "postgres"
    postgres_db_password: str = ""
    postgres_db_host: str = "localhost"
    postgres_db_port: int = 5432

    secret_key: str
    jwt_access_expires: int = 86400  # seconds
    jwt_refresh_expires: int = 172800  # seconds

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_db_user}:{self.postgres_db_password}"
            f"@{self.postgres_db_host}:{self.postgres_db_port}/{self.postgres_db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
