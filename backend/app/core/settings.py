from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "BeautyLens AI"
    API_VERSION: str = "v1"

    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024

    ALLOWED_IMAGE_TYPES: tuple[str, ...] = (
        "image/jpeg",
        "image/png",
        "image/webp",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
