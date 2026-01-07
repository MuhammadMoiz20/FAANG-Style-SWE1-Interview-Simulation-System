"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/interview_system"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    reload: bool = True

    # Environment
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
