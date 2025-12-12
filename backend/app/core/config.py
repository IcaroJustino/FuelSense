from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST: str = "db" 
    DB_PORT: int = 5432
    DB_USER: str = "user_api"
    DB_PASSWORD: str = "senha_secreta"
    DB_NAME: str = "user_api"
    API_TITLE: str = "API de Coleta de Combustível"
    API_VERSION: str = "1.0.0"

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()