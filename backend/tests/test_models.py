"""
測試 sales-lead-management 資料模型
遵循 TDD 原則：先寫測試，再實作程式碼
"""

import pytest
from datetime import datetime
from decimal import Decimal
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.database import Base
from app.models.base import (
    # 新增的 Enums
    InteractionType, ImportStatus, CustomerGrade,
    # 新增的 Models
    ImportBatch, Interaction, AIAnalysis, CustomerEvaluation, HealthCheckReport,
    # 現有 Models
    Customer, User
)


# ================================
# Test Fixtures
# ================================

@pytest.fixture
async def db_session():
    """建立測試資料庫 session"""
    # 使用記憶體資料庫進行測試
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def sample_customer(db_session: AsyncSession):
    """建立測試用客戶資料"""
    customer = Customer(
        company_name="測試公司",
        contact_person="測試聯絡人",
        contact_phone="0912345678",
        contact_email="test@test.com"
    )
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)
    return customer


# ================================
# Enum Tests
# ================================

def test_interaction_type_enum():
    """測試 InteractionType Enum 定義正確"""
    assert InteractionType.DOCUMENT == "document"
    assert InteractionType.AUDIO == "audio"
    assert InteractionType.STATUS_CHANGE == "status_change"


def test_import_status_enum():
    """測試 ImportStatus Enum 定義正確"""
    assert ImportStatus.PROCESSING == "processing"
    assert ImportStatus.COMPLETED == "completed"
    assert ImportStatus.FAILED == "failed"


def test_customer_grade_enum():
    """測試 CustomerGrade Enum 定義正確"""
    assert CustomerGrade.AA == "AA"
    assert CustomerGrade.A == "A"
    assert CustomerGrade.B == "B"
    assert CustomerGrade.C == "C"


# ================================
# ImportBatch Model Tests
# ================================

@pytest.mark.asyncio
async def test_import_batch_creation(db_session: AsyncSession):
    """測試 ImportBatch 模型可以建立"""
    batch = ImportBatch(
        file_name="test_import.xlsx",
        file_path="/path/to/file.xlsx",
        status=ImportStatus.PROCESSING,
        total_rows=100,
        success_count=0,
        fail_count=0,
        duplicate_count=0
    )

    db_session.add(batch)
    await db_session.commit()
    await db_session.refresh(batch)

    assert batch.id is not None
    assert batch.file_name == "test_import.xlsx"
    assert batch.status == ImportStatus.PROCESSING
    assert batch.total_rows == 100
    assert batch.created_at is not None


@pytest.mark.asyncio
async def test_import_batch_has_default_counters(db_session: AsyncSession):
    """測試 ImportBatch 有預設的計數器值"""
    batch = ImportBatch(
        file_name="test.xlsx",
        status=ImportStatus.PROCESSING
    )

    db_session.add(batch)
    await db_session.commit()
    await db_session.refresh(batch)

    assert batch.total_rows == 0
    assert batch.success_count == 0
    assert batch.fail_count == 0
    assert batch.duplicate_count == 0


# ================================
# Interaction Model Tests
# ================================

@pytest.mark.asyncio
async def test_interaction_creation(db_session: AsyncSession, sample_customer: Customer):
    """測試 Interaction 模型可以建立"""
    interaction = Interaction(
        customer_id=sample_customer.id,
        interaction_type=InteractionType.DOCUMENT,
        title="測試文檔",
        notes="測試備註",
        file_path="/path/to/document.pdf",
        file_name="document.pdf",
        file_size=1024000,
        file_type="application/pdf"
    )

    db_session.add(interaction)
    await db_session.commit()
    await db_session.refresh(interaction)

    assert interaction.id is not None
    assert interaction.customer_id == sample_customer.id
    assert interaction.interaction_type == InteractionType.DOCUMENT
    assert interaction.title == "測試文檔"
    assert interaction.file_name == "document.pdf"
    assert interaction.created_at is not None


@pytest.mark.asyncio
async def test_interaction_audio_with_transcript(db_session: AsyncSession, sample_customer: Customer):
    """測試音訊類型的 Interaction 可以儲存文字稿"""
    interaction = Interaction(
        customer_id=sample_customer.id,
        interaction_type=InteractionType.AUDIO,
        file_path="/path/to/audio.mp3",
        file_name="audio.mp3",
        file_size=5120000,
        file_type="audio/mpeg",
        audio_duration=300,  # 5 分鐘
        transcript_text="這是轉換後的文字稿內容"
    )

    db_session.add(interaction)
    await db_session.commit()
    await db_session.refresh(interaction)

    assert interaction.interaction_type == InteractionType.AUDIO
    assert interaction.audio_duration == 300
    assert interaction.transcript_text == "這是轉換後的文字稿內容"


@pytest.mark.asyncio
async def test_interaction_relationship_with_customer(db_session: AsyncSession, sample_customer: Customer):
    """測試 Interaction 與 Customer 的關聯"""
    interaction = Interaction(
        customer_id=sample_customer.id,
        interaction_type=InteractionType.DOCUMENT,
        title="關聯測試"
    )

    db_session.add(interaction)
    await db_session.commit()
    await db_session.refresh(interaction)

    # 測試關聯載入
    result = await db_session.execute(
        select(Interaction).where(Interaction.id == interaction.id)
    )
    loaded_interaction = result.scalar_one()

    assert loaded_interaction.customer_id == sample_customer.id


# ================================
# AIAnalysis Model Tests
# ================================

@pytest.mark.asyncio
async def test_ai_analysis_creation(db_session: AsyncSession, sample_customer: Customer):
    """測試 AIAnalysis 模型可以建立"""
    # 先建立一個 interaction
    interaction = Interaction(
        customer_id=sample_customer.id,
        interaction_type=InteractionType.AUDIO,
        transcript_text="測試對話內容"
    )
    db_session.add(interaction)
    await db_session.commit()
    await db_session.refresh(interaction)

    # 建立 AI 分析結果
    ai_analysis = AIAnalysis(
        interaction_id=interaction.id,
        customer_id=sample_customer.id,
        matched_questions=[
            {
                "question_number": 1,
                "question_text": "您的公司名稱是什麼?",
                "answer": "測試公司",
                "confidence": 95,
                "evidence": "我們公司叫測試公司"
            }
        ],
        summary="對話摘要",
        coverage_rate=Decimal("30.00"),
        quality_score=85,
        is_aa_customer=True,
        aa_confidence=90,
        aa_score=88,
        aa_reasons=["物件數量充足", "數位化程度高"],
        ai_model_version="gpt-4o-mini"
    )

    db_session.add(ai_analysis)
    await db_session.commit()
    await db_session.refresh(ai_analysis)

    assert ai_analysis.id is not None
    assert ai_analysis.interaction_id == interaction.id
    assert ai_analysis.customer_id == sample_customer.id
    assert len(ai_analysis.matched_questions) == 1
    assert ai_analysis.coverage_rate == Decimal("30.00")
    assert ai_analysis.quality_score == 85
    assert ai_analysis.is_aa_customer is True


@pytest.mark.asyncio
async def test_ai_analysis_extracted_info(db_session: AsyncSession, sample_customer: Customer):
    """測試 AIAnalysis 可以儲存提取的客戶資訊"""
    interaction = Interaction(
        customer_id=sample_customer.id,
        interaction_type=InteractionType.AUDIO
    )
    db_session.add(interaction)
    await db_session.commit()
    await db_session.refresh(interaction)

    ai_analysis = AIAnalysis(
        interaction_id=interaction.id,
        customer_id=sample_customer.id,
        matched_questions=[],
        extracted_info={
            "company_name": "新測試公司",
            "property_count": 150,
            "staff_count": 8,
            "business_type": "包租",
            "pain_points": ["人力不足", "系統老舊"]
        }
    )

    db_session.add(ai_analysis)
    await db_session.commit()
    await db_session.refresh(ai_analysis)

    assert ai_analysis.extracted_info is not None
    assert ai_analysis.extracted_info["company_name"] == "新測試公司"
    assert ai_analysis.extracted_info["property_count"] == 150


# ================================
# CustomerEvaluation Model Tests
# ================================

@pytest.mark.asyncio
async def test_customer_evaluation_creation(db_session: AsyncSession, sample_customer: Customer):
    """測試 CustomerEvaluation 模型可以建立"""
    evaluation = CustomerEvaluation(
        customer_id=sample_customer.id,
        grade=CustomerGrade.AA,
        score=92,
        evaluation_data={
            "property_count": 150,
            "digitalization_score": 85,
            "growth_intent": "strong",
            "decision_power": "high"
        },
        criteria_version="1.0.0",
        notes="高價值客戶，建議優先跟進"
    )

    db_session.add(evaluation)
    await db_session.commit()
    await db_session.refresh(evaluation)

    assert evaluation.id is not None
    assert evaluation.customer_id == sample_customer.id
    assert evaluation.grade == CustomerGrade.AA
    assert evaluation.score == 92
    assert evaluation.evaluation_data["property_count"] == 150
    assert evaluation.created_at is not None


@pytest.mark.asyncio
async def test_customer_evaluation_with_ai_analysis(db_session: AsyncSession, sample_customer: Customer):
    """測試 CustomerEvaluation 可以關聯 AIAnalysis"""
    # 建立 interaction 和 ai_analysis
    interaction = Interaction(
        customer_id=sample_customer.id,
        interaction_type=InteractionType.AUDIO
    )
    db_session.add(interaction)
    await db_session.commit()
    await db_session.refresh(interaction)

    ai_analysis = AIAnalysis(
        interaction_id=interaction.id,
        customer_id=sample_customer.id,
        matched_questions=[],
        is_aa_customer=True
    )
    db_session.add(ai_analysis)
    await db_session.commit()
    await db_session.refresh(ai_analysis)

    # 建立評估並關聯 AI 分析
    evaluation = CustomerEvaluation(
        customer_id=sample_customer.id,
        ai_analysis_id=ai_analysis.id,
        grade=CustomerGrade.AA,
        score=90,
        evaluation_data={}
    )

    db_session.add(evaluation)
    await db_session.commit()
    await db_session.refresh(evaluation)

    assert evaluation.ai_analysis_id == ai_analysis.id


# ================================
# HealthCheckReport Model Tests
# ================================

@pytest.mark.asyncio
async def test_health_check_report_creation(db_session: AsyncSession, sample_customer: Customer):
    """測試 HealthCheckReport 模型可以建立"""
    # 先建立評估記錄
    evaluation = CustomerEvaluation(
        customer_id=sample_customer.id,
        grade=CustomerGrade.AA,
        score=90,
        evaluation_data={}
    )
    db_session.add(evaluation)
    await db_session.commit()
    await db_session.refresh(evaluation)

    # 建立健檢報告
    report = HealthCheckReport(
        customer_id=sample_customer.id,
        evaluation_id=evaluation.id,
        report_title="測試公司_客戶健檢報告_2026-03-27",
        report_content={
            "customer_name": "測試公司",
            "grade": "AA",
            "score": 90,
            "questions": []
        },
        file_path="/storage/reports/2026-03-27/report_123.xlsx",
        file_format="xlsx"
    )

    db_session.add(report)
    await db_session.commit()
    await db_session.refresh(report)

    assert report.id is not None
    assert report.customer_id == sample_customer.id
    assert report.evaluation_id == evaluation.id
    assert report.report_title == "測試公司_客戶健檢報告_2026-03-27"
    assert report.file_format == "xlsx"
    assert report.created_at is not None


@pytest.mark.asyncio
async def test_health_check_report_content_structure(db_session: AsyncSession, sample_customer: Customer):
    """測試 HealthCheckReport 的報告內容結構"""
    evaluation = CustomerEvaluation(
        customer_id=sample_customer.id,
        grade=CustomerGrade.A,
        score=75,
        evaluation_data={}
    )
    db_session.add(evaluation)
    await db_session.commit()
    await db_session.refresh(evaluation)

    report = HealthCheckReport(
        customer_id=sample_customer.id,
        evaluation_id=evaluation.id,
        report_title="完整報告",
        report_content={
            "customer_info": {
                "name": "測試公司",
                "phone": "0912345678",
                "email": "test@test.com"
            },
            "evaluation": {
                "grade": "A",
                "score": 75,
                "criteria_version": "1.0.0"
            },
            "questions": [
                {
                    "number": 1,
                    "text": "問題內容",
                    "answer": "客戶回答",
                    "discussed": True
                }
            ]
        },
        file_path="/storage/reports/report.xlsx",
        file_format="xlsx"
    )

    db_session.add(report)
    await db_session.commit()
    await db_session.refresh(report)

    assert "customer_info" in report.report_content
    assert "evaluation" in report.report_content
    assert "questions" in report.report_content
    assert report.report_content["customer_info"]["name"] == "測試公司"


# ================================
# Model Relationships Tests
# ================================

@pytest.mark.asyncio
async def test_customer_has_import_batch_relationship(db_session: AsyncSession):
    """測試 Customer 可以關聯到 ImportBatch"""
    # 建立 import batch
    batch = ImportBatch(
        file_name="customers_import.xlsx",
        status=ImportStatus.COMPLETED,
        total_rows=10,
        success_count=10
    )
    db_session.add(batch)
    await db_session.commit()
    await db_session.refresh(batch)

    # 建立 customer 並關聯到 batch
    customer = Customer(
        company_name="批次匯入客戶",
        contact_phone="0911111111",
        import_batch_id=batch.id,
        ad_source="3特點輪播廣告"
    )
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)

    assert customer.import_batch_id == batch.id
    assert customer.ad_source == "3特點輪播廣告"


@pytest.mark.asyncio
async def test_cascade_delete_interactions(db_session: AsyncSession, sample_customer: Customer):
    """測試刪除客戶時級聯刪除互動記錄"""
    # 建立多個互動記錄
    interaction1 = Interaction(
        customer_id=sample_customer.id,
        interaction_type=InteractionType.DOCUMENT
    )
    interaction2 = Interaction(
        customer_id=sample_customer.id,
        interaction_type=InteractionType.AUDIO
    )

    db_session.add_all([interaction1, interaction2])
    await db_session.commit()

    # 刪除客戶
    await db_session.delete(sample_customer)
    await db_session.commit()

    # 驗證互動記錄也被刪除
    result = await db_session.execute(
        select(Interaction).where(Interaction.customer_id == sample_customer.id)
    )
    interactions = result.scalars().all()

    assert len(interactions) == 0


# ================================
# Index Tests (驗證索引定義正確)
# ================================

@pytest.mark.asyncio
async def test_interaction_indexes_defined(db_session: AsyncSession):
    """測試 Interaction 的索引定義正確"""
    from sqlalchemy import inspect

    inspector = inspect(db_session.bind)
    indexes = inspector.get_indexes('interactions')

    index_names = [idx['name'] for idx in indexes]

    # 驗證關鍵索引存在
    assert any('customer_id' in idx['name'] or
              any(col == 'customer_id' for col in idx.get('column_names', []))
              for idx in indexes)


# ================================
# UUID Generation Tests
# ================================

@pytest.mark.asyncio
async def test_models_generate_uuid_automatically(db_session: AsyncSession, sample_customer: Customer):
    """測試所有新模型都自動生成 UUID"""
    batch = ImportBatch(file_name="test.xlsx", status=ImportStatus.PROCESSING)
    interaction = Interaction(customer_id=sample_customer.id, interaction_type=InteractionType.DOCUMENT)

    db_session.add_all([batch, interaction])
    await db_session.commit()

    # 驗證 UUID 格式正確（36 字元）
    assert len(batch.id) == 36
    assert len(interaction.id) == 36
    assert '-' in batch.id  # UUID 格式包含連字符


# ================================
# Timestamp Tests
# ================================

@pytest.mark.asyncio
async def test_models_have_automatic_timestamps(db_session: AsyncSession, sample_customer: Customer):
    """測試所有新模型都有自動時間戳記"""
    interaction = Interaction(
        customer_id=sample_customer.id,
        interaction_type=InteractionType.DOCUMENT
    )

    db_session.add(interaction)
    await db_session.commit()
    await db_session.refresh(interaction)

    assert interaction.created_at is not None
    assert interaction.updated_at is not None
    assert isinstance(interaction.created_at, datetime)
    assert isinstance(interaction.updated_at, datetime)
