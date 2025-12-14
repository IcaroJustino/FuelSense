import json
import time 
from typing import Callable, Any, List, Optional
from functools import lru_cache, wraps 
from decimal import Decimal
import redis
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

@lru_cache()
def get_redis_settings() -> RedisSettings:
    return RedisSettings()

def get_redis_client() -> redis.Redis:
    settings = get_redis_settings()
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True 
        )
        r.ping() 
        return r
    except redis.exceptions.ConnectionError:
        print("AVISO: Erro ao conectar ao Redis. O cache está desativado.")
        return None 

REDIS_CLIENT = get_redis_client()
DEFAULT_TTL = 3600  # 1 hora (Time To Live)
LAST_UPDATE_KEY = "dashboard:last_data_ingestion"

def json_default_converter(obj):
    if isinstance(obj, Decimal):
        # Converte Decimal para float para ser serializável
        return float(obj) 
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')


def cached_data(cache_key_prefix: str, ttl: int = DEFAULT_TTL):
    def decorator(func: Callable) -> Callable:
        @wraps(func) 
        def wrapper(*args, **kwargs) -> Any:
            key_parts = [cache_key_prefix]
            for k, v in kwargs.items():
                if k not in ['db', 'current_user'] and v is not None:
                    str_v = str(v) 
                    key_parts.append(f"{k}:{str_v}")
            
            cache_key = ":".join(key_parts)
            
            if REDIS_CLIENT:
                cached_result = REDIS_CLIENT.get(cache_key)
                if cached_result:
                    print(f"CACHE HIT: {cache_key}")
                    return json.loads(cached_result) 
            
            print(f"CACHE MISS: {cache_key}")
            db_result = func(*args, **kwargs)

            if REDIS_CLIENT and db_result:
                try:
                    if isinstance(db_result, list):
                        data_to_cache = [item.model_dump() for item in db_result]
                    elif hasattr(db_result, 'model_dump'):
                        data_to_cache = db_result.model_dump()
                    else:
                        data_to_cache = db_result

                    serialized_data = json.dumps(
                        data_to_cache, 
                        default=json_default_converter
                    )
                
                except Exception as e:
                    print(f"ERRO DE SERIALIZAÇÃO NO CACHE para {cache_key}: {e}")
                    serialized_data = None 
                    
                if serialized_data:
                    REDIS_CLIENT.setex(cache_key, ttl, serialized_data)
                
            return db_result
        
        return wrapper
        
    return decorator

def invalidate_dashboard_cache(keys_to_delete: List[str]):
    if REDIS_CLIENT:
        full_keys = [f"kpi_{key}" for key in keys_to_delete]
        deleted_count = REDIS_CLIENT.delete(*full_keys)
        print(f"CACHE INVALIDATED: {deleted_count} chaves excluídas do Redis.")
    else:
        print("AVISO: Redis não está ativo. Não foi possível invalidar o cache.")

def set_last_update_timestamp():
    if REDIS_CLIENT:
        timestamp = int(time.time())
        REDIS_CLIENT.set(LAST_UPDATE_KEY, timestamp)

def get_last_update_timestamp() -> Optional[int]:
    if REDIS_CLIENT:
        ts_str = REDIS_CLIENT.get(LAST_UPDATE_KEY)
        if ts_str:
            try:
                return int(ts_str)
            except ValueError:
                return None
    return None