#!/bin/bash
# Alembic 本地執行腳本
# 用於在本地環境執行 alembic 命令（連接到 Docker 中的資料庫）

export DATABASE_URL="postgresql+asyncpg://postgres:postgres123@localhost:5434/sales_performance"

# 執行 alembic 命令
python3 -m alembic "$@"
