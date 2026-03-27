"""Alembic 環境配置"""
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio
import os
import sys

# 將 app 加入 Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Alembic Config 物件
config = context.config

# 設定日誌
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 匯入 Base 和所有模型
from app.core.database import Base
from app.models.base import (
    User, Customer, Visit, Contract, PerformanceMetric,
    QuestionTemplate, AaCustomerCriteria
)

# 設定 metadata
target_metadata = Base.metadata

# 從環境變數讀取資料庫 URL
from app.core.config import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """在 'offline' 模式運行遷移"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """在 'online' 模式運行異步遷移"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """在 'online' 模式運行遷移"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
