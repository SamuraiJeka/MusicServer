from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_ECHO: bool
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_EXPIRES_MIN: int
    REFRESH_EXPIRES_DAY: int
    MINIO_ENDPOINT: str
    MINIO_PUBLIC_ENDPOINT: str | None = None
    MINIO_AUDIO_BUCKET: str
    MINIO_IMAGE_BUCKET: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    FRONTEND_URL: str

    @property
    def postgres_url(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file="../../.env",
        env_file_encoding="utf-8",
    )


settings = Settings() #type: ignore
