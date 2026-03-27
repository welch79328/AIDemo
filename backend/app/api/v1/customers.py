"""
客戶管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from app.core.database import get_db
from app.crud.customer import customer_crud
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
    CustomerStatistics,
    CustomerStageEnum,
    CustomerStatusEnum,
)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerResponse, status_code=201)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    建立新客戶

    - **company_name**: 公司名稱（必填）
    - **contact_person**: 聯絡人
    - **contact_phone**: 聯絡電話
    - **contact_email**: 聯絡信箱
    - **website**: 公司網站
    - **customer_stage**: 經營階段
    - **basic_info**: 基本資訊（JSON）
    """
    customer = await customer_crud.create(db, customer_data)
    return customer


@router.get("", response_model=CustomerListResponse)
async def get_customers(
    page: int = Query(1, ge=1, description="頁碼"),
    limit: int = Query(20, ge=1, le=100, description="每頁筆數"),
    search: Optional[str] = Query(None, description="搜尋關鍵字（公司名稱、聯絡人、電話）"),
    is_aa: Optional[bool] = Query(None, description="是否為 AA 客戶"),
    status: Optional[CustomerStatusEnum] = Query(None, description="客戶狀態"),
    stage: Optional[CustomerStageEnum] = Query(None, description="經營階段"),
    db: AsyncSession = Depends(get_db)
):
    """
    取得客戶列表（分頁）

    支援以下篩選條件：
    - **search**: 搜尋公司名稱、聯絡人、電話
    - **is_aa**: 篩選 AA 客戶
    - **status**: 按客戶狀態篩選
    - **stage**: 按經營階段篩選
    """
    customers, total = await customer_crud.get_list(
        db=db,
        page=page,
        limit=limit,
        search=search,
        is_aa=is_aa,
        status=status,
        stage=stage,
    )

    total_pages = math.ceil(total / limit) if total > 0 else 0

    return CustomerListResponse(
        customers=customers,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/statistics", response_model=CustomerStatistics)
async def get_customer_statistics(db: AsyncSession = Depends(get_db)):
    """
    取得客戶統計資料

    包含：
    - 總客戶數
    - AA 客戶數
    - 按經營階段分類
    - 按狀態分類
    - 平均成熟度評分
    """
    stats = await customer_crud.get_statistics(db)
    return CustomerStatistics(**stats)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    取得單一客戶詳情
    """
    customer = await customer_crud.get_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客戶不存在")
    return customer


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新客戶資料

    可更新的欄位：
    - 基本資料（公司名稱、聯絡資訊等）
    - 經營階段
    - 客戶狀態
    - 是否為 AA 客戶
    - 成熟度評分
    """
    customer = await customer_crud.update(db, customer_id, customer_data)
    if not customer:
        raise HTTPException(status_code=404, detail="客戶不存在")
    return customer


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    刪除客戶

    注意：此操作無法復原
    """
    success = await customer_crud.delete(db, customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="客戶不存在")
    return None
