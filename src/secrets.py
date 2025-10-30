from pydantic_settings import BaseSettings
from pydantic import ConfigDict 

class Secrets(BaseSettings):
    ORACLE_USER: str = "system"
    ORACLE_PASSWORD: str = "Password123"
    ORACLE_DSN: str = "localhost:1521/XE"
    APP_PORT: int = 8000

    model_config = ConfigDict(env_file=".env")

secrets = Secrets()
