"""
拜訪記錄相關的 Pydantic Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


# Enums
class VisitTypeEnum(str, Enum):
    """拜訪類型"""
    FIRST_VISIT = "first_visit"    # 一訪
    SECOND_VISIT = "second_visit"  # 二訪


class VisitStatusEnum(str, Enum):
    """拜訪狀態"""
    SCHEDULED = "scheduled"  # 已排程
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


# Base Schema
class VisitBase(BaseModel):
    """拜訪記錄基礎 Schema"""
    customer_id: str = Field(..., description="客戶 ID")
    visit_type: VisitTypeEnum = Field(..., description="拜訪類型")
    visit_date: datetime = Field(..., description="拜訪日期")
    visit_status: VisitStatusEnum = Field(default=VisitStatusEnum.SCHEDULED, description="拜訪狀態")


# Create Schema
class VisitCreate(VisitBase):
    """建立拜訪記錄 Schema"""
    questionnaire_data: Optional[dict] = Field(None, description="問卷資料（JSON）")
    notes: Optional[str] = Field(None, description="備註")
    next_action: Optional[str] = Field(None, description="下一步行動")
    next_visit_date: Optional[datetime] = Field(None, description="下次拜訪日期")

    # ============ AI 整合欄位 ============
    conversation_transcript: Optional[str] = Field(None, description="對談逐字稿")
    ai_analyzed: Optional[bool] = Field(False, description="是否經 AI 分析")
    interaction_id: Optional[str] = Field(None, description="關聯的 Interaction ID")
    ai_analysis_id: Optional[str] = Field(None, description="關聯的 AIAnalysis ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_id": "uuid-string",
                "visit_type": "first_visit",
                "visit_date": "2026-03-20T10:00:00Z",
                "visit_status": "completed",
                "questionnaire_data": {
                    "A1": "有",
                    "A2": "100-200",
                    "B1": "PURE_RENTAL"
                },
                "notes": "客戶很有興趣，準備進入二訪",
                "next_action": "準備二訪簡報",
                "next_visit_date": "2026-03-27T14:00:00Z"
            }
        }
    )


# Update Schema
class VisitUpdate(BaseModel):
    """更新拜訪記錄 Schema"""
    visit_type: Optional[VisitTypeEnum] = None
    visit_date: Optional[datetime] = None
    visit_status: Optional[VisitStatusEnum] = None
    questionnaire_data: Optional[dict] = None
    notes: Optional[str] = None
    next_action: Optional[str] = None
    next_visit_date: Optional[datetime] = None

    # ============ AI 整合欄位 ============
    conversation_transcript: Optional[str] = None
    ai_analyzed: Optional[bool] = None
    interaction_id: Optional[str] = None
    ai_analysis_id: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "visit_status": "completed",
                "questionnaire_data": {
                    "A1": "有",
                    "A2": "100-200"
                },
                "notes": "已完成一訪"
            }
        }
    )


# Response Schema
class VisitResponse(VisitBase):
    """拜訪記錄回應 Schema"""
    id: str
    questionnaire_data: Optional[dict] = None
    notes: Optional[str] = None
    next_action: Optional[str] = None
    next_visit_date: Optional[datetime] = None

    # ============ AI 整合欄位 ============
    conversation_transcript: Optional[str] = None
    ai_analyzed: Optional[bool] = False
    interaction_id: Optional[str] = None
    ai_analysis_id: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "uuid-string",
                "customer_id": "uuid-string",
                "visit_type": "first_visit",
                "visit_date": "2026-03-20T10:00:00Z",
                "visit_status": "completed",
                "questionnaire_data": {"A1": "有", "A2": "100-200"},
                "notes": "客戶很有興趣",
                "next_action": "準備二訪",
                "next_visit_date": "2026-03-27T14:00:00Z",
                "created_at": "2026-03-20T10:00:00Z",
                "updated_at": "2026-03-20T10:00:00Z"
            }
        }
    )


# List Item Schema
class VisitListItem(BaseModel):
    """拜訪列表項目 Schema"""
    id: str
    customer_id: str
    visit_type: VisitTypeEnum
    visit_date: datetime
    visit_status: VisitStatusEnum
    notes: Optional[str] = None
    next_visit_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# List Response Schema (with customer info)
class VisitWithCustomer(VisitListItem):
    """拜訪記錄（含客戶資訊）"""
    customer_name: Optional[str] = None  # 從 relationship 取得


class VisitListResponse(BaseModel):
    """拜訪列表回應 Schema"""
    visits: list[VisitListItem]
    total: int
    page: int
    limit: int
    total_pages: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "visits": [
                    {
                        "id": "uuid-1",
                        "customer_id": "uuid-customer-1",
                        "visit_type": "first_visit",
                        "visit_date": "2026-03-20T10:00:00Z",
                        "visit_status": "completed",
                        "notes": "客戶很有興趣",
                        "next_visit_date": "2026-03-27T14:00:00Z",
                        "created_at": "2026-03-20T10:00:00Z",
                        "updated_at": "2026-03-20T10:00:00Z"
                    }
                ],
                "total": 15,
                "page": 1,
                "limit": 20,
                "total_pages": 1
            }
        }
    )


# Statistics Schema
class VisitStatistics(BaseModel):
    """拜訪統計 Schema"""
    total_visits: int = Field(description="總拜訪數")
    first_visits: int = Field(description="一訪數量")
    second_visits: int = Field(description="二訪數量")
    completed_visits: int = Field(description="已完成拜訪數")
    scheduled_visits: int = Field(description="已排程拜訪數")
    by_status: dict[str, int] = Field(description="按狀態分類")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_visits": 50,
                "first_visits": 30,
                "second_visits": 20,
                "completed_visits": 45,
                "scheduled_visits": 5,
                "by_status": {
                    "scheduled": 5,
                    "completed": 45,
                    "cancelled": 0
                }
            }
        }
    )
