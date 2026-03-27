"""
拜訪記錄 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from app.core.database import get_db
from app.crud.visit import visit_crud
from app.schemas.visit import (
    VisitCreate,
    VisitUpdate,
    VisitResponse,
    VisitListResponse,
    VisitStatistics,
    VisitTypeEnum,
    VisitStatusEnum,
)

router = APIRouter(prefix="/visits", tags=["visits"])


@router.post("", response_model=VisitResponse, status_code=201)
async def create_visit(
    visit_data: VisitCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    建立拜訪記錄

    - **customer_id**: 客戶 ID（必填）
    - **visit_type**: 拜訪類型（first_visit/second_visit）
    - **visit_date**: 拜訪日期
    - **visit_status**: 拜訪狀態（scheduled/completed/cancelled）
    - **questionnaire_data**: 問卷資料（JSON）
    - **notes**: 備註
    - **next_action**: 下一步行動
    - **next_visit_date**: 下次拜訪日期
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Creating visit with data: {visit_data.model_dump()}")

    visit = await visit_crud.create(db, visit_data)
    return visit


@router.get("", response_model=VisitListResponse)
async def get_visits(
    page: int = Query(1, ge=1, description="頁碼"),
    limit: int = Query(20, ge=1, le=100, description="每頁筆數"),
    customer_id: Optional[str] = Query(None, description="客戶 ID"),
    visit_type: Optional[VisitTypeEnum] = Query(None, description="拜訪類型"),
    visit_status: Optional[VisitStatusEnum] = Query(None, description="拜訪狀態"),
    db: AsyncSession = Depends(get_db)
):
    """
    取得拜訪記錄列表（分頁）

    支援以下篩選條件：
    - **customer_id**: 篩選特定客戶的拜訪記錄
    - **visit_type**: 按拜訪類型篩選
    - **visit_status**: 按拜訪狀態篩選
    """
    visits, total = await visit_crud.get_list(
        db=db,
        page=page,
        limit=limit,
        customer_id=customer_id,
        visit_type=visit_type,
        visit_status=visit_status,
    )

    total_pages = math.ceil(total / limit) if total > 0 else 0

    return VisitListResponse(
        visits=visits,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/statistics", response_model=VisitStatistics)
async def get_visit_statistics(db: AsyncSession = Depends(get_db)):
    """
    取得拜訪統計資料

    包含：
    - 總拜訪數
    - 一訪/二訪數量
    - 已完成/已排程拜訪數
    - 按狀態分類
    """
    stats = await visit_crud.get_statistics(db)
    return VisitStatistics(**stats)


@router.get("/{visit_id}", response_model=VisitResponse)
async def get_visit(
    visit_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    取得單一拜訪記錄詳情
    """
    visit = await visit_crud.get_by_id(db, visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="拜訪記錄不存在")
    return visit


@router.patch("/{visit_id}", response_model=VisitResponse)
async def update_visit(
    visit_id: str,
    visit_data: VisitUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新拜訪記錄

    可更新的欄位：
    - 拜訪類型、日期、狀態
    - 問卷資料
    - 備註、下一步行動
    - 下次拜訪日期
    """
    visit = await visit_crud.update(db, visit_id, visit_data)
    if not visit:
        raise HTTPException(status_code=404, detail="拜訪記錄不存在")
    return visit


@router.delete("/{visit_id}", status_code=204)
async def delete_visit(
    visit_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    刪除拜訪記錄

    注意：此操作無法復原
    """
    success = await visit_crud.delete(db, visit_id)
    if not success:
        raise HTTPException(status_code=404, detail="拜訪記錄不存在")
    return None


@router.get("/customer/{customer_id}/list", response_model=list[VisitResponse])
async def get_customer_visits(
    customer_id: str,
    visit_type: Optional[VisitTypeEnum] = Query(None, description="拜訪類型"),
    db: AsyncSession = Depends(get_db)
):
    """
    取得特定客戶的所有拜訪記錄

    - **customer_id**: 客戶 ID
    - **visit_type**: 可選，篩選拜訪類型
    """
    visits = await visit_crud.get_by_customer(db, customer_id, visit_type)
    return visits
