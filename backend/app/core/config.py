from pydantic_settings import BaseSettings
from typing import List
import json

class Settings(BaseSettings):
    PROJECT_NAME: str = "Retail Intelligence Platform"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    SECRET_KEY: str = "supersecretkey_change_in_production"

    DATABASE_URL: str = "postgresql+asyncpg://retail_user:retail_pass@localhost:5432/retail_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:8080"]'

    @property
    def cors_origins_list(self) -> List[str]:
        try:
            return json.loads(self.CORS_ORIGINS)
        except Exception:
            return ["http://localhost:3000"]

    NUM_STORES: int = 100
    NUM_PRODUCTS: int = 1000
    TRANSACTIONS_PER_MINUTE: int = 50

    LOW_STOCK_THRESHOLD: int = 20
    CRITICAL_STOCK_THRESHOLD: int = 10
    REORDER_MULTIPLIER: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()