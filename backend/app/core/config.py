from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Attributes:
        API_V1_PREFIX: API version prefix
        PROJECT_NAME: Name of the project
        DEBUG: Debug mode flag
        BACKEND_CORS_ORIGINS: List of allowed CORS origins
        DATABASE_URL: PostgreSQL database URL
    """

    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "EV Charger Simulator"
    DEBUG: bool = True
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    @classmethod
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        if isinstance(v, list):
            return v
        raise ValueError(v)

    DATABASE_URL: PostgresDsn

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
