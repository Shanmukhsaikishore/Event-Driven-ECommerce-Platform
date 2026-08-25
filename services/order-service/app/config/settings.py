from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str
    kafka_bootstrap_servers: str
    PRODUCT_SERVICE_URL: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()