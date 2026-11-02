from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://gaitmate:gaitmate_dev@localhost:5432/gaitmate"
    web_origin: str = "http://localhost:5173"


settings = Settings()
