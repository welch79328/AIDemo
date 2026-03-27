# Backend Dockerfile - FastAPI + Python 3.12 (MVP 簡化版)
FROM python:3.12-slim

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製依賴文件
COPY requirements.txt requirements-dev.txt ./

# 安裝 Python 依賴
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

# 複製應用程式碼
COPY . .

# 暴露端口
EXPOSE 8000

# 啟動命令（支援熱重載）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
