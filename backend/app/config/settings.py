from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class Settings(BaseSettings):

    # Existing project settings
    HUGGING_FACE_API_KEY: str

    # Safety settings
    ENABLE_PII: bool = True
    ENABLE_TOXICITY: bool = True
    ENABLE_INJECTION: bool = True
    ENABLE_POLICY: bool = True

    TOXICITY_THRESHOLD: float = 0.6
    INJECTION_THRESHOLD: float = 0.7

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()