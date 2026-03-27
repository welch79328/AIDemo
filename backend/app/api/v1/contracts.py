"""
簽約記錄 API 路由
"""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.contract import contract_crud
from app.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractListResponse,
    ContractStatistics,
    ContractKPIProgress,
    ContractQueryParams
)
from app.models.base import ContractType

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.post("", response_model=ContractResponse, status_code=201)
async def create_contract(
    contract_data: ContractCreate,
    db: AsyncSession = Depends(get_db)
):
    """建立簽約記錄"""
    contract = await contract_crud.create(db, contract_data)
    return contract


@router.get("", response_model=ContractListResponse)
async def get_contracts(
    page: int = Query(1, ge=1, description="頁碼"),
    limit: int = Query(20, ge=1, le=100, description="每頁筆數"),
    customer_id: Optional[str] = Query(None, description="客戶 ID"),
    contract_type: Optional[ContractType] = Query(None, description="合約類型"),
    onboarding_success: Optional[bool] = Query(None, description="導入成功狀態"),
    date_from: Optional[date] = Query(None, description="簽約日期起"),
    date_to: Optional[date] = Query(None, description="簽約日期迄"),
    db: AsyncSession = Depends(get_db)
):
    """取得簽約記錄列表（支援分頁與篩選）"""
    params = ContractQueryParams(
        page=page,
        limit=limit,
        customer_id=customer_id,
        contract_type=contract_type,
        onboarding_success=onboarding_success,
        date_from=date_from,
        date_to=date_to
    )

    contracts, total = await contract_crud.get_list(db, params)

    return ContractListResponse(
        contracts=contracts,
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit
    )


@router.get("/statistics", response_model=ContractStatistics)
async def get_contract_statistics(db: AsyncSession = Depends(get_db)):
    """取得簽約統計"""
    statistics = await contract_crud.get_statistics(db)
    return statistics


@router.get("/kpi-progress", response_model=list[ContractKPIProgress])
async def get_kpi_progress(db: AsyncSession = Depends(get_db)):
    """取得所有簽約的 KPI 進度"""
    kpi_progress_list = await contract_crud.get_kpi_progress_list(db)
    return kpi_progress_list


@router.get("/customer/{customer_id}/list", response_model=list[ContractResponse])
async def get_customer_contracts(
    customer_id: str,
    contract_type: Optional[ContractType] = Query(None, description="合約類型"),
    db: AsyncSession = Depends(get_db)
):
    """取得特定客戶的簽約記錄"""
    contracts = await contract_crud.get_by_customer(db, customer_id, contract_type)
    return contracts


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(contract_id: str, db: AsyncSession = Depends(get_db)):
    """取得簽約記錄詳情"""
    contract = await contract_crud.get_by_id(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="簽約記錄不存在")
    return contract


@router.patch("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: str,
    contract_data: ContractUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新簽約記錄"""
    contract = await contract_crud.update(db, contract_id, contract_data)
    if not contract:
        raise HTTPException(status_code=404, detail="簽約記錄不存在")
    return contract


@router.delete("/{contract_id}", status_code=204)
async def delete_contract(contract_id: str, db: AsyncSession = Depends(get_db)):
    """刪除簽約記錄"""
    success = await contract_crud.delete(db, contract_id)
    if not success:
        raise HTTPException(status_code=404, detail="簽約記錄不存在")
    return None
