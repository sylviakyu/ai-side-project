from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Environment-driven configuration for the FastAPI service."""

    api_port: int = Field(8000, env="API_PORT")
    db_url: str = Field(
        "mysql+asyncmy://user:pass@mysql:3306/taskflow",
        env="DB_URL",
    )
    redis_url: str = Field("redis://redis:6379/0", env="REDIS_URL")
    rabbitmq_url: str = Field("amqp://guest:guest@rabbitmq:5672/", env="RABBITMQ_URL")
    rabbitmq_exchange: str = Field("task.topic", env="RABBITMQ_EXCHANGE")
    rabbitmq_routing_key: str = Field("task.created", env="RABBITMQ_ROUTING_KEY")
    db_echo: bool = Field(False, env="DB_ECHO")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
