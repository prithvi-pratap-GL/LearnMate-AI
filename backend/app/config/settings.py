from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HUGGING_FACE_API_KEY: str
    DEBUG: bool=True
    class Config:
        env_file = ".env"

settings = Settings()
