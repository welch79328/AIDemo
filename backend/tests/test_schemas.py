"""
測試 sales-lead-management Pydantic Schemas
遵循 TDD 原則：先寫測試，再實作 schemas
"""

import pytest
from datetime import datetime
from decimal import Decimal
from pydantic import ValidationError

# 這些 import 會在 GREEN 階段實作後才能正常運作
try:
    from app.schemas.lead import (
        ImportOptions,
        DuplicateInfo,
        ImportError,
        ImportBatchSummary,
        ImportHistoryResponse,
        LeadImportResponse
    )
    from app.schemas.interaction import (
        InteractionTypeEnum,
        InteractionCreate,
        InteractionResponse,
        InteractionUploadResponse,
        InteractionListResponse
    )
    from app.schemas.report import (
        ReportGenerateRequest,
        ReportGenerateResponse,
        ReportEmailRequest,
        ReportEmailResponse,
        BatchExportRequest
    )
    from app.schemas.ai_analysis import (
        AudioTranscribeRequest,
        AudioTranscribeResponse
    )
    SCHEMAS_AVAILABLE = True
except ImportError:
    SCHEMAS_AVAILABLE = False


# ================================
# Lead Schemas Tests
# ================================

@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_import_options_schema():
    """測試 ImportOptions schema"""
    options = ImportOptions(
        skip_duplicates=True,
        update_existing=False,
        dry_run=False
    )

    assert options.skip_duplicates is True
    assert options.update_existing is False
    assert options.dry_run is False


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_import_options_defaults():
    """測試 ImportOptions 預設值"""
    options = ImportOptions()

    assert options.skip_duplicates is False
    assert options.update_existing is False
    assert options.dry_run is False


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_duplicate_info_schema():
    """測試 DuplicateInfo schema"""
    duplicate = DuplicateInfo(
        row_number=5,
        customer_name="測試公司",
        phone="0912345678",
        existing_customer_id="customer-123"
    )

    assert duplicate.row_number == 5
    assert duplicate.customer_name == "測試公司"
    assert duplicate.phone == "0912345678"
    assert duplicate.existing_customer_id == "customer-123"


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_import_error_schema():
    """測試 ImportError schema"""
    error = ImportError(
        row_number=10,
        error_type="validation_error",
        error_message="缺少必填欄位：公司名稱",
        row_data={"phone": "0912345678"}
    )

    assert error.row_number == 10
    assert error.error_type == "validation_error"
    assert "公司名稱" in error.error_message
    assert error.row_data["phone"] == "0912345678"


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_import_batch_summary_schema():
    """測試 ImportBatchSummary schema"""
    batch = ImportBatchSummary(
        id="batch-123",
        file_name="customers.xlsx",
        status="completed",
        total_rows=100,
        success_count=95,
        fail_count=5,
        created_at=datetime.now(),
        created_by="user-123"
    )

    assert batch.id == "batch-123"
    assert batch.file_name == "customers.xlsx"
    assert batch.status == "completed"
    assert batch.total_rows == 100
    assert batch.success_count == 95


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_lead_import_response_schema():
    """測試 LeadImportResponse schema"""
    response = LeadImportResponse(
        batch_id="batch-123",
        status="processing",
        total_rows=100,
        success_count=0,
        fail_count=0,
        duplicate_count=0,
        duplicates=[],
        errors=[]
    )

    assert response.batch_id == "batch-123"
    assert response.status == "processing"
    assert isinstance(response.duplicates, list)
    assert isinstance(response.errors, list)


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_lead_import_response_with_duplicates():
    """測試包含重複資料的 LeadImportResponse"""
    duplicate = DuplicateInfo(
        row_number=5,
        customer_name="測試公司",
        phone="0912345678",
        existing_customer_id="customer-123"
    )

    response = LeadImportResponse(
        batch_id="batch-123",
        status="completed",
        total_rows=100,
        success_count=95,
        fail_count=0,
        duplicate_count=5,
        duplicates=[duplicate],
        errors=[]
    )

    assert response.duplicate_count == 5
    assert len(response.duplicates) == 1
    assert response.duplicates[0].customer_name == "測試公司"


# ================================
# Interaction Schemas Tests
# ================================

@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_interaction_type_enum():
    """測試 InteractionTypeEnum"""
    assert InteractionTypeEnum.DOCUMENT == "document"
    assert InteractionTypeEnum.AUDIO == "audio"
    assert InteractionTypeEnum.STATUS_CHANGE == "status_change"


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_interaction_create_schema():
    """測試 InteractionCreate schema"""
    interaction = InteractionCreate(
        customer_id="customer-123",
        interaction_type=InteractionTypeEnum.DOCUMENT,
        title="一訪文檔",
        notes="記錄一訪內容"
    )

    assert interaction.customer_id == "customer-123"
    assert interaction.interaction_type == InteractionTypeEnum.DOCUMENT
    assert interaction.title == "一訪文檔"


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_interaction_create_validation():
    """測試 InteractionCreate 必填欄位驗證"""
    with pytest.raises(ValidationError):
        InteractionCreate(
            # 缺少 customer_id 和 interaction_type
            title="測試"
        )


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_interaction_response_schema():
    """測試 InteractionResponse schema"""
    interaction = InteractionResponse(
        id="interaction-123",
        customer_id="customer-123",
        interaction_type="document",
        title="一訪文檔",
        notes="備註",
        created_at=datetime.now(),
        created_by="user-123"
    )

    assert interaction.id == "interaction-123"
    assert interaction.customer_id == "customer-123"
    assert isinstance(interaction.created_at, datetime)


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_interaction_upload_response_schema():
    """測試 InteractionUploadResponse schema"""
    response = InteractionUploadResponse(
        id="interaction-123",
        customer_id="customer-123",
        interaction_type="audio",
        file_name="recording.mp3",
        file_size=5242880,
        file_type="audio/mpeg",
        audio_duration=300,
        created_at=datetime.now()
    )

    assert response.file_name == "recording.mp3"
    assert response.file_size == 5242880
    assert response.audio_duration == 300


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_interaction_list_response_schema():
    """測試 InteractionListResponse schema"""
    interaction1 = InteractionResponse(
        id="int-1",
        customer_id="customer-123",
        interaction_type="document",
        created_at=datetime.now()
    )

    response = InteractionListResponse(
        interactions=[interaction1],
        total=1,
        page=1,
        limit=20
    )

    assert len(response.interactions) == 1
    assert response.total == 1
    assert response.page == 1


# ================================
# AI Analysis Schemas Tests
# ================================

@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_audio_transcribe_request_schema():
    """測試 AudioTranscribeRequest schema"""
    request = AudioTranscribeRequest(
        interaction_id="interaction-123",
        language="zh"
    )

    assert request.interaction_id == "interaction-123"
    assert request.language == "zh"


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_audio_transcribe_request_default_language():
    """測試 AudioTranscribeRequest 預設語言"""
    request = AudioTranscribeRequest(
        interaction_id="interaction-123"
    )

    assert request.language == "zh"  # 預設應為中文


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_audio_transcribe_response_schema():
    """測試 AudioTranscribeResponse schema"""
    response = AudioTranscribeResponse(
        interaction_id="interaction-123",
        transcript_text="這是轉換後的文字稿",
        audio_duration=300,
        processing_time=45.5,
        ai_model_version="whisper-1"
    )

    assert response.interaction_id == "interaction-123"
    assert "文字稿" in response.transcript_text
    assert response.audio_duration == 300
    assert response.processing_time == 45.5


# ================================
# Report Schemas Tests
# ================================

@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_report_generate_request_schema():
    """測試 ReportGenerateRequest schema"""
    request = ReportGenerateRequest(
        customer_id="customer-123",
        format="xlsx",
        include_ai_analysis=True
    )

    assert request.customer_id == "customer-123"
    assert request.format == "xlsx"
    assert request.include_ai_analysis is True


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_report_generate_request_defaults():
    """測試 ReportGenerateRequest 預設值"""
    request = ReportGenerateRequest(
        customer_id="customer-123"
    )

    assert request.format == "xlsx"  # 預設格式
    assert request.include_ai_analysis is True  # 預設包含 AI 分析


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_report_generate_request_format_validation():
    """測試 ReportGenerateRequest 格式驗證"""
    # 應該只接受 xlsx 或 pdf
    with pytest.raises(ValidationError):
        ReportGenerateRequest(
            customer_id="customer-123",
            format="doc"  # 不支援的格式
        )


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_report_generate_response_schema():
    """測試 ReportGenerateResponse schema"""
    response = ReportGenerateResponse(
        report_id="report-123",
        customer_id="customer-123",
        file_path="/storage/reports/2026-03-27/report_123.xlsx",
        file_format="xlsx",
        created_at=datetime.now()
    )

    assert response.report_id == "report-123"
    assert response.file_format == "xlsx"
    assert ".xlsx" in response.file_path


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_report_email_request_schema():
    """測試 ReportEmailRequest schema"""
    request = ReportEmailRequest(
        report_id="report-123",
        recipient_email="client@example.com",
        subject="客戶健檢報告",
        message="附件為貴公司的健檢報告"
    )

    assert request.report_id == "report-123"
    assert request.recipient_email == "client@example.com"
    assert "報告" in request.subject


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_report_email_request_email_validation():
    """測試 ReportEmailRequest email 格式驗證"""
    with pytest.raises(ValidationError):
        ReportEmailRequest(
            report_id="report-123",
            recipient_email="invalid-email"  # 無效的 email 格式
        )


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_report_email_response_schema():
    """測試 ReportEmailResponse schema"""
    response = ReportEmailResponse(
        success=True,
        message="Email 發送成功",
        sent_at=datetime.now()
    )

    assert response.success is True
    assert "成功" in response.message


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_batch_export_request_schema():
    """測試 BatchExportRequest schema"""
    request = BatchExportRequest(
        customer_ids=["customer-1", "customer-2", "customer-3"],
        format="xlsx"
    )

    assert len(request.customer_ids) == 3
    assert request.format == "xlsx"


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_batch_export_request_max_customers():
    """測試 BatchExportRequest 最大客戶數限制"""
    # 應該限制最多 50 個客戶
    with pytest.raises(ValidationError):
        BatchExportRequest(
            customer_ids=[f"customer-{i}" for i in range(51)],  # 51 個客戶
            format="xlsx"
        )


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_batch_export_request_min_customers():
    """測試 BatchExportRequest 至少需要一個客戶"""
    with pytest.raises(ValidationError):
        BatchExportRequest(
            customer_ids=[],  # 空列表
            format="xlsx"
        )


# ================================
# Schema 互相引用測試
# ================================

@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_import_history_response_pagination():
    """測試 ImportHistoryResponse 分頁功能"""
    batch1 = ImportBatchSummary(
        id="batch-1",
        file_name="file1.xlsx",
        status="completed",
        total_rows=100,
        success_count=100,
        fail_count=0,
        created_at=datetime.now()
    )

    response = ImportHistoryResponse(
        batches=[batch1],
        total=10,
        page=1,
        limit=20,
        total_pages=1
    )

    assert len(response.batches) == 1
    assert response.total == 10
    assert response.total_pages == 1


# ================================
# Schema JSON 序列化測試
# ================================

@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_schema_json_serialization():
    """測試 schema 可以正確序列化為 JSON"""
    interaction = InteractionResponse(
        id="int-1",
        customer_id="customer-123",
        interaction_type="document",
        created_at=datetime.now()
    )

    # 應該可以轉換為 JSON
    json_str = interaction.model_dump_json()
    assert "int-1" in json_str
    assert "customer-123" in json_str


@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not yet implemented")
def test_schema_from_dict():
    """測試 schema 可以從字典建立"""
    data = {
        "customer_id": "customer-123",
        "interaction_type": "document",
        "title": "測試文檔"
    }

    interaction = InteractionCreate(**data)
    assert interaction.customer_id == "customer-123"
    assert interaction.title == "測試文檔"
