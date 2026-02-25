from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    DATABASE_URL: str = "postgresql://erp_user:erp_pass@localhost:5432/erp_db"
    SECRET_KEY: str = "insecure-dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    FIRST_ADMIN_EMAIL: str = "admin@fincepto.com"
    FIRST_ADMIN_PASSWORD: str = "Admin@1234"


settings = Settings()
