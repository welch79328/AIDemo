"""
客戶相關的 Pydantic Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


# Enums
class CustomerStageEnum(str, Enum):
    """客戶經營階段"""
    INDIVIDUAL = "individual"                    # 個人戶
    PREPARING_COMPANY = "preparing_company"      # 要準備成立公司
    NEW_COMPANY = "new_company"                  # 剛成立公司
    SCALING_UP = "scaling_up"                    # 物件量增加想數位升級


class CustomerStatusEnum(str, Enum):
    """客戶狀態"""
    CONTACTED = "contacted"                          # 已接觸
    FIRST_VISIT_SCHEDULED = "first_visit_scheduled"  # 已排程一訪
    FIRST_VISIT_DONE = "first_visit_done"            # 已完成一訪
    SECOND_VISIT_SCHEDULED = "second_visit_scheduled"# 已排程二訪
    SECOND_VISIT_DONE = "second_visit_done"          # 已完成二訪
    NEGOTIATING = "negotiating"                      # 洽談中
    SIGNED = "signed"                                # 已簽約
    LOST = "lost"                                    # 未成交


# Base Schema
class CustomerBase(BaseModel):
    """客戶基礎 Schema"""
    company_name: str = Field(..., min_length=1, max_length=255, description="公司名稱")
    contact_person: Optional[str] = Field(None, max_length=100, description="聯絡人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="聯絡電話")
    contact_email: Optional[str] = Field(None, max_length=255, description="聯絡信箱")
    website: Optional[str] = Field(None, max_length=255, description="公司網站")
    customer_stage: Optional[CustomerStageEnum] = Field(None, description="經營階段")


# Create Schema
class CustomerCreate(CustomerBase):
    """建立客戶 Schema"""
    basic_info: Optional[dict] = Field(None, description="基本資訊（JSON）")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_name": "XX 包租代管公司",
                "contact_person": "張經理",
                "contact_phone": "0912-345-678",
                "contact_email": "manager@example.com",
                "website": "https://www.example.com",
                "customer_stage": "scaling_up",
                "basic_info": {
                    "has_line_oa": True,
                    "company_background": "PURE_RENTAL"
                }
            }
        }
    )


# Update Schema
class CustomerUpdate(BaseModel):
    """更新客戶 Schema"""
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    customer_stage: Optional[CustomerStageEnum] = None
    current_status: Optional[CustomerStatusEnum] = None
    basic_info: Optional[dict] = None
    is_aa_customer: Optional[bool] = None
    maturity_score: Optional[int] = Field(None, ge=0, le=100, description="成熟度評分 0-100")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "contact_phone": "0988-999-888",
                "current_status": "first_visit_done",
                "maturity_score": 85
            }
        }
    )


# Response Schema
class CustomerResponse(CustomerBase):
    """客戶回應 Schema"""
    id: str
    is_aa_customer: bool
    maturity_score: Optional[int] = None
    current_status: CustomerStatusEnum
    basic_info: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "uuid-string",
                "company_name": "XX 包租代管公司",
                "contact_person": "張經理",
                "contact_phone": "0912-345-678",
                "contact_email": "manager@example.com",
                "website": "https://www.example.com",
                "customer_stage": "scaling_up",
                "is_aa_customer": True,
                "maturity_score": 85,
                "current_status": "first_visit_done",
                "basic_info": {"has_line_oa": True},
                "created_at": "2026-03-20T10:00:00Z",
                "updated_at": "2026-03-20T10:00:00Z"
            }
        }
    )


# List Item Schema (簡化版，用於列表顯示)
class CustomerListItem(BaseModel):
    """客戶列表項目 Schema"""
    id: str
    company_name: str
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    is_aa_customer: bool
    customer_stage: Optional[CustomerStageEnum] = None
    maturity_score: Optional[int] = None
    current_status: CustomerStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# List Response Schema
class CustomerListResponse(BaseModel):
    """客戶列表回應 Schema"""
    customers: list[CustomerListItem]
    total: int
    page: int
    limit: int
    total_pages: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customers": [
                    {
                        "id": "uuid-1",
                        "company_name": "XX 包租代管公司",
                        "contact_person": "張經理",
                        "contact_phone": "0912-345-678",
                        "is_aa_customer": True,
                        "customer_stage": "scaling_up",
                        "maturity_score": 85,
                        "current_status": "first_visit_done",
                        "created_at": "2026-03-20T10:00:00Z",
                        "updated_at": "2026-03-20T10:00:00Z"
                    }
                ],
                "total": 45,
                "page": 1,
                "limit": 20,
                "total_pages": 3
            }
        }
    )


# Statistics Schema
class CustomerStatistics(BaseModel):
    """客戶統計 Schema"""
    total_customers: int = Field(description="總客戶數")
    aa_customers: int = Field(description="AA 客戶數")
    by_stage: dict[str, int] = Field(description="按經營階段分類")
    by_status: dict[str, int] = Field(description="按狀態分類")
    average_maturity_score: Optional[float] = Field(None, description="平均成熟度評分")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_customers": 45,
                "aa_customers": 12,
                "by_stage": {
                    "individual": 5,
                    "preparing_company": 8,
                    "new_company": 12,
                    "scaling_up": 20
                },
                "by_status": {
                    "contacted": 10,
                    "first_visit_done": 15,
                    "second_visit_done": 12,
                    "signed": 8
                },
                "average_maturity_score": 68.5
            }
        }
    )
