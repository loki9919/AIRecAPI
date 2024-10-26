from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Secure Product API"
    API_KEYS: List[str]
    DATABASE_URL: str
    GROQ_API_KEY: str
    class Config:
        env_file = ".env"

settings = Settings()
