"""
API v1 路由模組
"""
from fastapi import APIRouter
from app.api.v1 import customers, visits, contracts, ai_analysis, leads, interactions, reports

api_router = APIRouter(prefix="/api/v1")

# 註冊各模組路由
api_router.include_router(customers.router)
api_router.include_router(visits.router)
api_router.include_router(contracts.router)
api_router.include_router(ai_analysis.router)
api_router.include_router(leads.router)
api_router.include_router(interactions.router)
api_router.include_router(reports.router)
