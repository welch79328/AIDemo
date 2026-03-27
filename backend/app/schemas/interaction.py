"""
客戶互動記錄相關的 Pydantic Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ================================
# Enums
# ================================

class InteractionTypeEnum(str, Enum):
    """互動類型"""
    DOCUMENT = "document"
    AUDIO = "audio"
    STATUS_CHANGE = "status_change"


# ================================
# Base Schema
# ================================

class InteractionBase(BaseModel):
    """互動記錄基礎 Schema"""
    customer_id: str = Field(..., description="客戶 ID")
    interaction_type: InteractionTypeEnum = Field(..., description="互動類型")
    title: Optional[str] = Field(None, max_length=255, description="標題")
    notes: Optional[str] = Field(None, description="備註")


# ================================
# Create Schema
# ================================

class InteractionCreate(InteractionBase):
    """建立互動記錄 Schema（非檔案上傳）"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_id": "customer-123",
                "interaction_type": "status_change",
                "title": "狀態變更：已完成一訪",
                "notes": "客戶對產品表示興趣，已安排二訪"
            }
        }
    )


# ================================
# Response Schemas
# ================================

class InteractionResponse(BaseModel):
    """互動記錄回應 Schema"""
    id: str = Field(..., description="互動記錄 ID")
    customer_id: str = Field(..., description="客戶 ID")
    interaction_type: str = Field(..., description="互動類型")
    title: Optional[str] = Field(None, description="標題")
    notes: Optional[str] = Field(None, description="備註")
    file_path: Optional[str] = Field(None, description="檔案路徑")
    file_name: Optional[str] = Field(None, description="檔案名稱")
    file_size: Optional[int] = Field(None, description="檔案大小（bytes）")
    file_type: Optional[str] = Field(None, description="檔案類型")
    audio_duration: Optional[int] = Field(None, description="音訊時長（秒）")
    transcript_text: Optional[str] = Field(None, description="文字稿")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: Optional[datetime] = Field(None, description="更新時間")
    created_by: Optional[str] = Field(None, description="建立者 ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "interaction-123",
                "customer_id": "customer-123",
                "interaction_type": "document",
                "title": "一訪會議記錄",
                "notes": "討論物件管理需求",
                "file_path": "/storage/interactions/documents/doc_123.pdf",
                "file_name": "meeting_notes.pdf",
                "file_size": 1024000,
                "file_type": "application/pdf",
                "created_at": "2026-03-27T10:00:00Z"
            }
        }
    )


class InteractionUploadResponse(BaseModel):
    """檔案上傳後的互動記錄回應"""
    id: str = Field(..., description="互動記錄 ID")
    customer_id: str = Field(..., description="客戶 ID")
    interaction_type: str = Field(..., description="互動類型")
    title: Optional[str] = Field(None, description="標題")
    file_path: Optional[str] = Field(None, description="檔案路徑")
    file_name: str = Field(..., description="檔案名稱")
    file_size: int = Field(..., description="檔案大小（bytes）", ge=0)
    audio_duration: Optional[int] = Field(None, description="音訊時長（秒）", ge=0)
    notes: Optional[str] = Field(None, description="備註")
    created_at: datetime = Field(..., description="建立時間")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "interaction-123",
                "customer_id": "customer-123",
                "interaction_type": "audio",
                "title": "客戶訪談錄音",
                "file_path": "interactions/audios/recording_123.mp3",
                "file_name": "recording_20260327.mp3",
                "file_size": 5242880,
                "audio_duration": 300,
                "notes": "討論物件管理需求",
                "created_at": "2026-03-27T10:00:00Z"
            }
        }
    )


class InteractionListResponse(BaseModel):
    """互動記錄列表回應"""
    interactions: List[InteractionResponse] = Field(..., description="互動記錄列表")
    total: int = Field(..., description="總筆數", ge=0)
    page: int = Field(..., description="當前頁碼", ge=1)
    limit: int = Field(..., description="每頁筆數", ge=1)
    total_pages: int = Field(..., description="總頁數", ge=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "interactions": [],
                "total": 10,
                "page": 1,
                "limit": 20,
                "total_pages": 1
            }
        }
    )
