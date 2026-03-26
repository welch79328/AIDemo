"""
應用程式配置
使用 Pydantic Settings 管理環境變數
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """應用程式設定"""

    # 應用基本資訊
    APP_NAME: str = "業務行動成效評估系統"
    DEBUG: bool = True

    # 資料庫設定
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres123@postgres:5432/sales_performance"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    # Redis 設定（可選,用於快取）
    REDIS_URL: str = "redis://redis:6379/0"

    # CORS 設定（使用字符串，避免環境變數解析問題）
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:8080,http://localhost:8081,http://localhost:3000"

    # OpenAI API 設定
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """將 CORS_ORIGINS 字符串轉換為列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# 建立全域設定實例
settings = Settings()
