"""
Pytest 配置與 fixtures
"""
import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

# 設置測試環境變數（在導入 app 之前）
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("OPENAI_API_KEY", "test-key")

# 現在可以安全導入模型
from app.core.database import Base
# 導入所有模型以確保它們被註冊到 Base.metadata
from app.models.base import (  # noqa: F401
    User, Customer, Visit, Contract, PerformanceMetric,
    QuestionTemplate, AaCustomerCriteria,
    ImportBatch, Interaction, AIAnalysis, CustomerEvaluation, HealthCheckReport
)


# 測試資料庫 URL（使用內存 SQLite）
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_engine():
    """創建測試用資料庫引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )

    # 創建所有資料表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 清理：刪除所有資料表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """創建測試用資料庫 session"""
    async_session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def async_client(db_session):
    """創建測試用 HTTP 客戶端"""
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.core.database import get_db

    # Override get_db dependency to use test db_session
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

    # Clean up
    app.dependency_overrides.clear()
