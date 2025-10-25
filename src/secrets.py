from pydantic_settings import BaseSettings

class Secrets(BaseSettings):
    ORACLE_USER: str = "admin"
    ORACLE_PASSWORD: str = "password"
    ORACLE_DSN:str = "localhost:1521/XE"

    class Config:
        env_file = ".env"


secrets = Secrets()

