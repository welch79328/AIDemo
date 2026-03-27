"""
資料庫連線設定
使用 SQLAlchemy 2.0 async engine
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 建立異步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # 連線池自動檢測
)

# 建立 Session 工廠
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Base class for models
class Base(DeclarativeBase):
    """SQLAlchemy Base Class"""
    pass


# 依賴注入：取得資料庫 session
async def get_db():
    """
    資料庫 session 依賴注入
    使用方式: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# 初始化資料庫（建立所有表）
async def init_db():
    """初始化資料庫表"""
    async with engine.begin() as conn:
        # 匯入所有模型以確保表被建立
        from app.models import user, customer, visit, contract, performance_metric

        # 建立所有表
        await conn.run_sync(Base.metadata.create_all)
        logger.info("資料庫表建立完成")


# 關閉資料庫連線
async def close_db():
    """關閉資料庫連線"""
    await engine.dispose()
    logger.info("資料庫連線已關閉")
