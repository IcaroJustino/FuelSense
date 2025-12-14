import redis
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class RedisSettings(BaseSettings):
    REDIS_HOST: str = "localhost" 
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

@lru_cache()
def get_redis_settings():
    return RedisSettings()

# Inicializa o cliente Redis
def get_redis_client() -> redis.Redis:
    settings = get_redis_settings()
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        # Testa a conexão
        r.ping() 
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"Erro ao conectar ao Redis: {e}")
        return None