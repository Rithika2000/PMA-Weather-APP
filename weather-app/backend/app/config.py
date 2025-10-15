from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = "sqlite:///./weather.db"
    YT_API_KEY: str | None = None
    CSE_API_KEY: str | None = None
    CSE_CX: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
