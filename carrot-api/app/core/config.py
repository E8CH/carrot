from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30일
    ALLOWED_ORIGINS: str = ""  # 쉼표 구분 추가 오리진 (Railway 배포 URL)


settings = Settings()
