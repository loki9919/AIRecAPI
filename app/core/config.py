from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Secure Product API"
    API_KEYS: List[str]
    DATABASE_URL: str


    class Config:
        env_file = ".env"

# Create an instance of the Settings class
settings = Settings()
