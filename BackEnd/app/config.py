from pydantic import Field
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    database_url:str = Field(..., alias="DATABASE_URL")
    echo_sql: bool = Field(..., alias="ECHO")
    secret_key: str = Field(..., alias="SECRET_KEY")
    algorithm: str  = Field(..., alias="ALGORITHM")
    access_token_expire_minutes: int = Field(..., alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()    

