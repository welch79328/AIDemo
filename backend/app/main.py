"""
FastAPI 應用程式主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 建立 FastAPI 應用
app = FastAPI(
    title=settings.APP_NAME,
    description="業務行動成效評估系統 - MVP 版本",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 中介層
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康檢查端點
@app.get("/health", tags=["健康檢查"])
async def health_check():
    """健康檢查端點"""
    return JSONResponse(
        content={
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "version": "1.0.0"
        }
    )


# 根路徑
@app.get("/", tags=["根路徑"])
async def root():
    """根路徑，返回 API 資訊"""
    return {
        "message": "業務行動成效評估系統 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# 註冊 API 路由
from app.api.v1 import api_router
app.include_router(api_router)

# TODO: 待實作的路由模組
# from app.api.v1 import visits, contracts, dashboard
# app.include_router(visits.router, prefix="/api/v1/visits", tags=["拜訪記錄"])
# app.include_router(contracts.router, prefix="/api/v1/contracts", tags=["簽約管理"])
# app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["儀表板"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
