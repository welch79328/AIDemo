"""
客戶健檢報告相關的 Pydantic Schemas
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator, EmailStr
from typing import Optional, List
from datetime import datetime


# ================================
# Report Generate Schemas
# ================================

class ReportGenerateRequest(BaseModel):
    """生成報告請求"""
    customer_id: str = Field(..., description="客戶 ID")
    evaluation_id: Optional[str] = Field(None, description="評估記錄 ID（不指定則使用最新）")
    format: str = Field(default="xlsx", description="報告格式")
    include_ai_analysis: bool = Field(default=True, description="包含 AI 分析結果")

    @field_validator('format')
    @classmethod
    def validate_format(cls, v: str) -> str:
        """驗證報告格式"""
        if v not in ['xlsx', 'pdf']:
            raise ValueError('報告格式只支援 xlsx 或 pdf')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_id": "customer-123",
                "evaluation_id": None,
                "format": "xlsx",
                "include_ai_analysis": True
            }
        }
    )


class ReportGenerateResponse(BaseModel):
    """生成報告回應"""
    report_id: str = Field(..., description="報告 ID")
    customer_id: str = Field(..., description="客戶 ID")
    file_path: str = Field(..., description="檔案路徑")
    file_format: str = Field(..., description="檔案格式")
    created_at: datetime = Field(..., description="建立時間")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "report_id": "report-123",
                "customer_id": "customer-123",
                "file_path": "/storage/reports/2026-03-27/report_123.xlsx",
                "file_format": "xlsx",
                "created_at": "2026-03-27T10:00:00Z"
            }
        }
    )


# ================================
# Email Schemas
# ================================

class ReportEmailRequest(BaseModel):
    """Email 分享報告請求"""
    report_id: str = Field(..., description="報告 ID")
    recipient_email: EmailStr = Field(..., description="收件人 Email")
    subject: Optional[str] = Field(None, description="Email 主旨")
    message: Optional[str] = Field(None, description="Email 內容")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "report_id": "report-123",
                "recipient_email": "client@example.com",
                "subject": "貴公司客戶健檢報告",
                "message": "附件為貴公司的客戶健檢報告，請查收。"
            }
        }
    )


class ReportEmailResponse(BaseModel):
    """Email 發送回應"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="訊息")
    sent_at: datetime = Field(..., description="發送時間")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Email 發送成功",
                "sent_at": "2026-03-27T10:00:00Z"
            }
        }
    )


# ================================
# Batch Export Schemas
# ================================

class BatchExportRequest(BaseModel):
    """批次匯出報告請求"""
    customer_ids: List[str] = Field(..., description="客戶 ID 列表", min_length=1, max_length=50)
    format: str = Field(default="xlsx", description="報告格式")

    @field_validator('format')
    @classmethod
    def validate_format(cls, v: str) -> str:
        """驗證報告格式"""
        if v not in ['xlsx', 'pdf']:
            raise ValueError('報告格式只支援 xlsx 或 pdf')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_ids": ["customer-1", "customer-2", "customer-3"],
                "format": "xlsx"
            }
        }
    )


# ================================
# Report Query Schemas
# ================================

class ReportResponse(BaseModel):
    """報告詳情回應"""
    id: str = Field(..., description="報告 ID")
    customer_id: str = Field(..., description="客戶 ID")
    evaluation_id: str = Field(..., description="評估記錄 ID")
    file_path: str = Field(..., description="檔案路徑")
    file_name: str = Field(..., description="檔案名稱")
    report_format: str = Field(..., description="報告格式")
    report_data: dict = Field(default_factory=dict, description="報告摘要資料")
    created_by: Optional[str] = Field(None, description="建立者 ID")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: datetime = Field(..., description="更新時間")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "report-123",
                "customer_id": "customer-123",
                "evaluation_id": "eval-123",
                "file_path": "/storage/reports/2026-03-27/report_123.xlsx",
                "file_name": "某公司_健檢報告_2026-03-27.xlsx",
                "report_format": "xlsx",
                "report_data": {
                    "customer_name": "某公司",
                    "grade": "A",
                    "score": 85.5,
                    "coverage_rate": 0.73
                },
                "created_by": None,
                "created_at": "2026-03-27T10:00:00Z",
                "updated_at": "2026-03-27T10:00:00Z"
            }
        }
    )


class ReportListResponse(BaseModel):
    """報告列表回應"""
    reports: List[ReportResponse] = Field(..., description="報告列表")
    total: int = Field(..., description="總數")
    page: int = Field(..., description="當前頁碼")
    limit: int = Field(..., description="每頁筆數")
    total_pages: int = Field(..., description="總頁數")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reports": [
                    {
                        "id": "report-123",
                        "customer_id": "customer-123",
                        "evaluation_id": "eval-123",
                        "file_path": "/storage/reports/2026-03-27/report_123.xlsx",
                        "file_name": "某公司_健檢報告_2026-03-27.xlsx",
                        "report_format": "xlsx",
                        "report_data": {},
                        "created_by": None,
                        "created_at": "2026-03-27T10:00:00Z",
                        "updated_at": "2026-03-27T10:00:00Z"
                    }
                ],
                "total": 100,
                "page": 1,
                "limit": 20,
                "total_pages": 5
            }
        }
    )
