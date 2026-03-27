"""
Excel 名單導入相關的 Pydantic Schemas
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ================================
# Enums
# ================================

class ImportStatusEnum(str, Enum):
    """導入狀態"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ================================
# Import Options
# ================================

class ImportOptions(BaseModel):
    """Excel 導入選項"""
    skip_duplicates: bool = Field(default=False, description="跳過重複資料")
    update_existing: bool = Field(default=False, description="更新現有資料")
    dry_run: bool = Field(default=False, description="乾運行（不實際導入）")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "skip_duplicates": False,
                "update_existing": False,
                "dry_run": False
            }
        }
    )


# ================================
# Duplicate & Error Info
# ================================

class DuplicateInfo(BaseModel):
    """重複資料資訊"""
    row_number: int = Field(..., description="Excel 列號", ge=1)
    customer_name: str = Field(..., description="客戶名稱")
    phone: str = Field(..., description="電話號碼")
    existing_customer_id: str = Field(..., description="現有客戶 ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "row_number": 5,
                "customer_name": "測試公司",
                "phone": "0912345678",
                "existing_customer_id": "customer-123"
            }
        }
    )


class ImportError(BaseModel):
    """導入錯誤資訊"""
    row_number: int = Field(..., description="Excel 列號", ge=1)
    error_type: str = Field(..., description="錯誤類型")
    error_message: str = Field(..., description="錯誤訊息")
    row_data: Dict[str, Any] = Field(..., description="該列資料")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "row_number": 10,
                "error_type": "validation_error",
                "error_message": "缺少必填欄位：公司名稱",
                "row_data": {"phone": "0912345678", "email": "test@test.com"}
            }
        }
    )


# ================================
# Import Batch Schemas
# ================================

class ImportBatchSummary(BaseModel):
    """導入批次摘要"""
    id: str = Field(..., description="批次 ID")
    file_name: str = Field(..., description="檔案名稱")
    status: str = Field(..., description="狀態")
    total_rows: int = Field(..., description="總列數", ge=0)
    success_count: int = Field(..., description="成功筆數", ge=0)
    fail_count: int = Field(..., description="失敗筆數", ge=0)
    created_at: datetime = Field(..., description="建立時間")
    created_by: Optional[str] = Field(None, description="建立者 ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "batch-123",
                "file_name": "customers_20260327.xlsx",
                "status": "completed",
                "total_rows": 100,
                "success_count": 95,
                "fail_count": 5,
                "created_at": "2026-03-27T10:00:00Z",
                "created_by": "user-123"
            }
        }
    )


class ImportHistoryResponse(BaseModel):
    """導入歷史回應"""
    batches: List[ImportBatchSummary] = Field(..., description="批次列表")
    total: int = Field(..., description="總筆數", ge=0)
    page: int = Field(..., description="當前頁碼", ge=1)
    limit: int = Field(..., description="每頁筆數", ge=1)
    total_pages: int = Field(..., description="總頁數", ge=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "batches": [],
                "total": 10,
                "page": 1,
                "limit": 20,
                "total_pages": 1
            }
        }
    )


# ================================
# Import Response
# ================================

class LeadImportResponse(BaseModel):
    """Excel 導入回應"""
    batch_id: str = Field(..., description="批次 ID")
    status: str = Field(..., description="狀態")
    total_rows: int = Field(..., description="總列數", ge=0)
    success_count: int = Field(..., description="成功筆數", ge=0)
    fail_count: int = Field(..., description="失敗筆數", ge=0)
    duplicate_count: int = Field(..., description="重複筆數", ge=0)
    duplicates: List[DuplicateInfo] = Field(default=[], description="重複資料列表")
    errors: List[ImportError] = Field(default=[], description="錯誤列表")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "batch_id": "batch-123",
                "status": "completed",
                "total_rows": 100,
                "success_count": 95,
                "fail_count": 5,
                "duplicate_count": 0,
                "duplicates": [],
                "errors": []
            }
        }
    )
