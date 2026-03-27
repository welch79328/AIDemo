"""
簽約記錄 Schema
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field
from app.models.base import ContractType


class ContractBase(BaseModel):
    """簽約記錄基礎 Schema"""
    customer_id: str = Field(..., description="客戶 ID")
    visit_id: Optional[str] = Field(None, description="關聯的拜訪記錄 ID")
    contract_date: date = Field(..., description="簽約日期")
    contract_type: ContractType = Field(..., description="合約類型")
    property_count: Optional[int] = Field(None, description="物件數量")
    monthly_value: Optional[Decimal] = Field(None, description="月費金額")


class ContractCreate(ContractBase):
    """建立簽約記錄 Schema"""
    # 導入 KPI (選填)
    kpi_property_upload_rate: Optional[Decimal] = Field(None, description="物件上傳率 (%)")
    kpi_contract_creation_rate: Optional[Decimal] = Field(None, description="合約建立率 (%)")
    kpi_billing_active: bool = Field(False, description="帳單已發送")
    kpi_payment_integrated: bool = Field(False, description="金流串接")
    kpi_notification_setup: bool = Field(False, description="自動通知")
    kpi_sop_established: bool = Field(False, description="SOP 建立")

    # 導入狀態 (選填)
    onboarding_success: bool = Field(False, description="導入成功")
    onboarding_date: Optional[date] = Field(None, description="導入完成日期")


class ContractUpdate(BaseModel):
    """更新簽約記錄 Schema"""
    visit_id: Optional[str] = Field(None, description="關聯的拜訪記錄 ID")
    contract_date: Optional[date] = Field(None, description="簽約日期")
    contract_type: Optional[ContractType] = Field(None, description="合約類型")
    property_count: Optional[int] = Field(None, description="物件數量")
    monthly_value: Optional[Decimal] = Field(None, description="月費金額")

    # 導入 KPI
    kpi_property_upload_rate: Optional[Decimal] = Field(None, description="物件上傳率 (%)")
    kpi_contract_creation_rate: Optional[Decimal] = Field(None, description="合約建立率 (%)")
    kpi_billing_active: Optional[bool] = Field(None, description="帳單已發送")
    kpi_payment_integrated: Optional[bool] = Field(None, description="金流串接")
    kpi_notification_setup: Optional[bool] = Field(None, description="自動通知")
    kpi_sop_established: Optional[bool] = Field(None, description="SOP 建立")

    # 導入狀態
    onboarding_success: Optional[bool] = Field(None, description="導入成功")
    onboarding_date: Optional[date] = Field(None, description="導入完成日期")


class ContractResponse(ContractBase):
    """簽約記錄回應 Schema"""
    id: str

    # 導入 KPI
    kpi_property_upload_rate: Optional[Decimal] = None
    kpi_contract_creation_rate: Optional[Decimal] = None
    kpi_billing_active: bool
    kpi_payment_integrated: bool
    kpi_notification_setup: bool
    kpi_sop_established: bool

    # 導入狀態
    onboarding_success: bool
    onboarding_date: Optional[date] = None

    # 時間戳記
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None

    model_config = {"from_attributes": True}


class ContractListItem(BaseModel):
    """簽約記錄列表項目 Schema"""
    id: str
    customer_id: str
    contract_date: date
    contract_type: ContractType
    property_count: Optional[int] = None
    monthly_value: Optional[Decimal] = None
    onboarding_success: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ContractListResponse(BaseModel):
    """簽約記錄列表回應 Schema"""
    contracts: list[ContractListItem]
    total: int
    page: int
    limit: int
    total_pages: int


class ContractStatistics(BaseModel):
    """簽約統計 Schema"""
    total_contracts: int = Field(..., description="總簽約數")
    package_rental_contracts: int = Field(..., description="包租簽約數")
    property_mgmt_contracts: int = Field(..., description="代管簽約數")
    sublease_contracts: int = Field(..., description="代租簽約數")
    hybrid_contracts: int = Field(..., description="混合簽約數")
    onboarding_success_count: int = Field(..., description="成功導入數")
    onboarding_success_rate: float = Field(..., description="導入成功率 (%)")
    avg_property_count: float = Field(..., description="平均物件數")
    total_monthly_value: Decimal = Field(..., description="總月費金額")
    by_type: dict[str, int] = Field(..., description="按類型統計")
    by_month: dict[str, int] = Field(..., description="按月份統計")


class ContractKPIProgress(BaseModel):
    """簽約 KPI 進度 Schema"""
    contract_id: str
    customer_name: str
    contract_date: date
    kpi_property_upload_rate: Optional[Decimal] = None
    kpi_contract_creation_rate: Optional[Decimal] = None
    kpi_billing_active: bool
    kpi_payment_integrated: bool
    kpi_notification_setup: bool
    kpi_sop_established: bool
    kpi_completion_rate: float = Field(..., description="KPI 完成率 (%)")
    onboarding_success: bool


class ContractQueryParams(BaseModel):
    """簽約查詢參數 Schema"""
    page: int = Field(1, description="頁碼")
    limit: int = Field(20, description="每頁筆數")
    customer_id: Optional[str] = Field(None, description="客戶 ID")
    contract_type: Optional[ContractType] = Field(None, description="合約類型")
    onboarding_success: Optional[bool] = Field(None, description="導入成功狀態")
    date_from: Optional[date] = Field(None, description="簽約日期起")
    date_to: Optional[date] = Field(None, description="簽約日期迄")
