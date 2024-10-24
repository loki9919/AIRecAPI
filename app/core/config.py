from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Secure Product API"
    API_KEYS: list[str]
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
