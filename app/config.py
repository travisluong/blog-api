from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    api_key: str
    jwt_secret: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
