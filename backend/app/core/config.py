from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Kanban API"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = str

    # Redis
    REDIS_URL: str = str

    # JWT
    SECRET_KEY: str = str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"] 

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
