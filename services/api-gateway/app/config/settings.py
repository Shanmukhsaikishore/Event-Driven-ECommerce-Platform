from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ORDER_SERVICE_URL: str
    PRODUCT_SERVICE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()