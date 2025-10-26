from pydantic_settings import BaseSettings

class Secrets(BaseSettings):
    ORACLE_USER: str = "system"
    ORACLE_PASSWORD: str = "12345@!@#$%"
    ORACLE_DSN:str = "localhost:1521/XE"
    APP_PORT: int = 8000

    class Config:
        env_file = ".env"


secrets = Secrets()

