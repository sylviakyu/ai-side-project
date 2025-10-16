from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Environment configuration for the worker service."""

    db_url: str = Field(
        "mysql+asyncmy://user:pass@mysql:3306/taskflow",
        env="DB_URL",
    )
    redis_url: str = Field("redis://redis:6379/0", env="REDIS_URL")
    rabbitmq_url: str = Field("amqp://guest:guest@rabbitmq:5672/", env="RABBITMQ_URL")
    rabbitmq_exchange: str = Field("task.topic", env="RABBITMQ_EXCHANGE")
    rabbitmq_queue: str = Field("task.created", env="RABBITMQ_QUEUE")
    rabbitmq_routing_key: str = Field("task.created", env="RABBITMQ_ROUTING_KEY")
    worker_prefetch: int = Field(8, env="WORKER_PREFETCH")
    rabbitmq_connect_attempts: int = Field(10, env="RABBITMQ_CONNECT_ATTEMPTS")
    rabbitmq_connect_backoff: float = Field(2.0, env="RABBITMQ_CONNECT_BACKOFF")
    db_connect_attempts: int = Field(10, env="DB_CONNECT_ATTEMPTS")
    db_connect_backoff: float = Field(2.0, env="DB_CONNECT_BACKOFF")
    db_echo: bool = Field(False, env="DB_ECHO")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
