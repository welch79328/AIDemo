"""
SQLAlchemy Database Models - 業務行動成效評估系統
資料庫: PostgreSQL
ORM: SQLAlchemy 2.0
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import (
    String, Integer, Boolean, DateTime, Date, Text, Numeric,
    ForeignKey, Index, JSON, Enum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid

# 從 database.py 導入 Base
from app.core.database import Base


# ================================
# Enum 定義
# ================================

class UserRole(str, PyEnum):
    """用戶角色"""
    SALES = "sales"          # 業務人員
    MANAGER = "manager"      # 主管
    ADMIN = "admin"          # 系統管理員


class CustomerStage(str, PyEnum):
    """客戶經營階段"""
    INDIVIDUAL = "individual"                    # 個人戶
    PREPARING_COMPANY = "preparing_company"      # 要準備成立公司
    NEW_COMPANY = "new_company"                  # 剛成立公司
    SCALING_UP = "scaling_up"                    # 物件量增加想數位升級


class CustomerStatus(str, PyEnum):
    """客戶狀態"""
    CONTACTED = "contacted"                          # 已接觸
    FIRST_VISIT_SCHEDULED = "first_visit_scheduled"  # 已排程一訪
    FIRST_VISIT_DONE = "first_visit_done"            # 已完成一訪
    SECOND_VISIT_SCHEDULED = "second_visit_scheduled"# 已排程二訪
    SECOND_VISIT_DONE = "second_visit_done"          # 已完成二訪
    NEGOTIATING = "negotiating"                      # 洽談中
    SIGNED = "signed"                                # 已簽約
    LOST = "lost"                                    # 未成交


class VisitType(str, PyEnum):
    """拜訪類型"""
    FIRST_VISIT = "first_visit"      # 一訪
    SECOND_VISIT = "second_visit"    # 二訪
    FOLLOW_UP = "follow_up"          # 追蹤拜訪


class VisitStatus(str, PyEnum):
    """拜訪狀態"""
    SCHEDULED = "scheduled"          # 已排程
    COMPLETED = "completed"          # 已完成
    CANCELLED = "cancelled"          # 已取消
    RESCHEDULED = "rescheduled"      # 已改期


class ContractType(str, PyEnum):
    """合約類型"""
    PACKAGE_RENTAL = "package_rental"    # 包租
    PROPERTY_MGMT = "property_mgmt"      # 代管
    SUBLEASE = "sublease"                # 代租
    HYBRID = "hybrid"                    # 混合


class MetricPeriod(str, PyEnum):
    """統計週期"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class QuestionCategory(str, PyEnum):
    """問卷分類"""
    A_BASIC_INFO = "a_basic_info"        # A 類：公司基本資料
    B_PROPERTY = "b_property"            # B 類：物件狀態與發展
    C_BUSINESS = "c_business"            # C 類：經營狀態
    D_DIGITAL = "d_digital"              # D 類：數位化程度


class QuestionPriority(str, PyEnum):
    """問題優先級"""
    REQUIRED = "required"                # 必問
    RECOMMENDED = "recommended"          # 建議
    OPTIONAL = "optional"                # 可選（Nice to have）


class QuestionType(str, PyEnum):
    """問題類型"""
    TEXT = "text"                        # 文字輸入
    TEXTAREA = "textarea"                # 長文字
    NUMBER = "number"                    # 數字
    SELECT = "select"                    # 單選
    MULTISELECT = "multiselect"          # 多選
    BOOLEAN = "boolean"                  # 是非題
    DATE = "date"                        # 日期
    URL = "url"                          # 網址


class InteractionType(str, PyEnum):
    """互動記錄類型"""
    DOCUMENT = "document"                # 文檔上傳
    AUDIO = "audio"                      # 錄音檔
    STATUS_CHANGE = "status_change"      # 狀態變更記錄


class ImportStatus(str, PyEnum):
    """導入狀態"""
    PROCESSING = "processing"            # 處理中
    COMPLETED = "completed"              # 已完成
    FAILED = "failed"                    # 失敗


class CustomerGrade(str, PyEnum):
    """客戶等級"""
    AA = "AA"                            # 高價值客戶
    A = "A"                              # 優質客戶
    B = "B"                              # 一般客戶
    C = "C"                              # 低價值客戶


# ================================
# 核心資料模型
# ================================

class User(Base):
    """用戶（業務人員）"""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.SALES)
    team: Mapped[Optional[str]] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 關聯
    customers: Mapped[list["Customer"]] = relationship(back_populates="creator")
    visits: Mapped[list["Visit"]] = relationship(back_populates="creator")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="creator")
    performance_metrics: Mapped[list["PerformanceMetric"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"


class Customer(Base):
    """客戶"""
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_person: Mapped[Optional[str]] = mapped_column(String(100))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20))
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    website: Mapped[Optional[str]] = mapped_column(String(255))

    # 分類與評分
    is_aa_customer: Mapped[bool] = mapped_column(Boolean, default=False)
    customer_stage: Mapped[Optional[CustomerStage]] = mapped_column(Enum(CustomerStage))
    maturity_score: Mapped[Optional[int]] = mapped_column(Integer)  # 0-100

    # 基本資訊（來自一訪 A 類問題，JSON 格式）
    basic_info: Mapped[Optional[dict]] = mapped_column(JSON)

    # 業務狀態
    current_status: Mapped[CustomerStatus] = mapped_column(Enum(CustomerStatus), default=CustomerStatus.CONTACTED)

    # ============ sales-lead-management 新增欄位 ============
    # 廣告來源
    ad_source: Mapped[Optional[str]] = mapped_column(String(100))

    # 導入批次
    import_batch_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("import_batches.id", ondelete="SET NULL"))

    # 追蹤資訊
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)  # MVP: nullable

    # 關聯
    creator: Mapped[Optional["User"]] = relationship(back_populates="customers")
    visits: Mapped[list["Visit"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="customer", cascade="all, delete-orphan")

    # ============ sales-lead-management 新增關聯 ============
    import_batch: Mapped[Optional["ImportBatch"]] = relationship(back_populates="customers")
    interactions: Mapped[list["Interaction"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
    evaluations: Mapped[list["CustomerEvaluation"]] = relationship(cascade="all, delete-orphan")
    reports: Mapped[list["HealthCheckReport"]] = relationship(cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_company_name', 'company_name'),
        Index('idx_is_aa_customer', 'is_aa_customer'),
        Index('idx_customer_stage', 'customer_stage'),
        Index('idx_current_status', 'current_status'),
        # sales-lead-management 新增索引
        Index('idx_ad_source', 'ad_source'),
        Index('idx_import_batch_id', 'import_batch_id'),
    )

    def __repr__(self):
        return f"<Customer(id={self.id}, company_name={self.company_name})>"


class Visit(Base):
    """拜訪記錄"""
    __tablename__ = "visits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"))
    visit_type: Mapped[VisitType] = mapped_column(Enum(VisitType))
    visit_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    visit_status: Mapped[VisitStatus] = mapped_column(Enum(VisitStatus))

    # 一訪資料（JSON 格式儲存）
    basic_info: Mapped[Optional[dict]] = mapped_column(JSON)          # A 類：公司基本資料
    property_status: Mapped[Optional[dict]] = mapped_column(JSON)     # B 類：物件狀態（一訪部分）

    # 二訪資料（JSON 格式儲存）
    development_plan: Mapped[Optional[dict]] = mapped_column(JSON)    # B 類：發展方向（二訪部分）
    business_status: Mapped[Optional[dict]] = mapped_column(JSON)     # C 類：經營狀態
    digitalization: Mapped[Optional[dict]] = mapped_column(JSON)      # D 類：數位化程度

    # MVP 簡化：統一問卷資料欄位
    questionnaire_data: Mapped[Optional[dict]] = mapped_column(JSON)  # 統一儲存所有問卷資料

    # ============ AI 分析整合 ============
    # 對談逐字稿
    conversation_transcript: Mapped[Optional[str]] = mapped_column(Text)

    # AI 分析標記
    ai_analyzed: Mapped[bool] = mapped_column(Boolean, default=False)

    # AI 分析關聯 (如果使用 Interaction/AIAnalysis)
    interaction_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("interactions.id", ondelete="SET NULL"))
    ai_analysis_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("ai_analyses.id", ondelete="SET NULL"))

    # 痛點與需求分析
    pain_points: Mapped[Optional[str]] = mapped_column(Text)
    client_needs: Mapped[Optional[str]] = mapped_column(Text)

    # 備註與下一步行動
    notes: Mapped[Optional[str]] = mapped_column(Text)
    next_action: Mapped[Optional[str]] = mapped_column(String(255))
    next_visit_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 追蹤資訊
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)  # MVP: nullable

    # 關聯
    customer: Mapped["Customer"] = relationship(back_populates="visits")
    creator: Mapped[Optional["User"]] = relationship(back_populates="visits")
    interaction: Mapped[Optional["Interaction"]] = relationship()
    ai_analysis: Mapped[Optional["AIAnalysis"]] = relationship()

    # 索引
    __table_args__ = (
        Index('idx_visit_customer_id', 'customer_id'),
        Index('idx_visit_date', 'visit_date'),
        Index('idx_visit_status', 'visit_status'),
    )

    def __repr__(self):
        return f"<Visit(id={self.id}, customer_id={self.customer_id}, visit_type={self.visit_type})>"


class Contract(Base):
    """簽約記錄"""
    __tablename__ = "contracts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"))
    visit_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("visits.id", ondelete="SET NULL"))

    contract_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    contract_type: Mapped[ContractType] = mapped_column(Enum(ContractType))
    property_count: Mapped[Optional[int]] = mapped_column(Integer)
    monthly_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    # 導入 KPI 追蹤（基於「導入成功KPIs」工作表）
    kpi_property_upload_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))      # 物件上傳率 (%)
    kpi_contract_creation_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))    # 合約建立率 (%)
    kpi_billing_active: Mapped[bool] = mapped_column(Boolean, default=False)                # 帳單已發送
    kpi_payment_integrated: Mapped[bool] = mapped_column(Boolean, default=False)            # 金流串接
    kpi_notification_setup: Mapped[bool] = mapped_column(Boolean, default=False)            # 自動通知
    kpi_sop_established: Mapped[bool] = mapped_column(Boolean, default=False)               # SOP 建立

    # 導入狀態
    onboarding_success: Mapped[bool] = mapped_column(Boolean, default=False)
    onboarding_date: Mapped[Optional[datetime]] = mapped_column(Date)

    # 追蹤資訊
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)  # MVP: nullable

    # 關聯
    customer: Mapped["Customer"] = relationship(back_populates="contracts")
    creator: Mapped[Optional["User"]] = relationship(back_populates="contracts")

    # 索引
    __table_args__ = (
        Index('idx_contract_customer_id', 'customer_id'),
        Index('idx_contract_date', 'contract_date'),
    )

    def __repr__(self):
        return f"<Contract(id={self.id}, customer_id={self.customer_id}, contract_type={self.contract_type})>"


class PerformanceMetric(Base):
    """業務績效指標（每日/每週/每月彙總）"""
    __tablename__ = "performance_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    metric_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    metric_period: Mapped[MetricPeriod] = mapped_column(Enum(MetricPeriod))

    # 活動指標
    total_visits: Mapped[int] = mapped_column(Integer, default=0)
    first_visits: Mapped[int] = mapped_column(Integer, default=0)
    second_visits: Mapped[int] = mapped_column(Integer, default=0)
    follow_up_visits: Mapped[int] = mapped_column(Integer, default=0)

    # 結果指標
    contracts_signed: Mapped[int] = mapped_column(Integer, default=0)
    aa_customers_acquired: Mapped[int] = mapped_column(Integer, default=0)

    # 轉換率（自動計算）
    conversion_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    # 追蹤資訊
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 關聯
    user: Mapped["User"] = relationship(back_populates="performance_metrics")

    # 索引與唯一約束
    __table_args__ = (
        Index('idx_user_metric_date', 'user_id', 'metric_date'),
        Index('idx_metric_date', 'metric_date'),
    )

    def __repr__(self):
        return f"<PerformanceMetric(user_id={self.user_id}, metric_date={self.metric_date}, period={self.metric_period})>"


# ================================
# sales-lead-management 資料模型
# ================================

class ImportBatch(Base):
    """Excel 導入批次記錄"""
    __tablename__ = "import_batches"

    # 主鍵
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 檔案資訊
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[Optional[str]] = mapped_column(String(500))

    # 導入結果
    status: Mapped[ImportStatus] = mapped_column(Enum(ImportStatus))
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    fail_count: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_count: Mapped[int] = mapped_column(Integer, default=0)

    # 錯誤記錄
    error_log: Mapped[Optional[dict]] = mapped_column(JSON)

    # 時間戳
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    # 關聯
    creator: Mapped[Optional["User"]] = relationship()
    customers: Mapped[list["Customer"]] = relationship(back_populates="import_batch")

    # 索引
    __table_args__ = (
        Index('idx_import_batch_status', 'status'),
        Index('idx_import_batch_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<ImportBatch(id={self.id}, file_name={self.file_name}, status={self.status})>"


class Interaction(Base):
    """客戶互動記錄（文檔、錄音、狀態變更）"""
    __tablename__ = "interactions"

    # 主鍵
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 外鍵
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"))

    # 互動類型與內容
    interaction_type: Mapped[InteractionType] = mapped_column(Enum(InteractionType))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # 檔案資訊
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    file_name: Mapped[Optional[str]] = mapped_column(String(255))
    file_size: Mapped[Optional[int]] = mapped_column(Integer)  # bytes
    file_type: Mapped[Optional[str]] = mapped_column(String(50))  # MIME type

    # 音訊特定欄位
    audio_duration: Mapped[Optional[int]] = mapped_column(Integer)  # seconds
    transcript_text: Mapped[Optional[str]] = mapped_column(Text)  # 轉換後的文字稿

    # 時間戳
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    # 關聯
    customer: Mapped["Customer"] = relationship(back_populates="interactions")
    creator: Mapped[Optional["User"]] = relationship()
    ai_analysis: Mapped[Optional["AIAnalysis"]] = relationship(back_populates="interaction", uselist=False)

    # 索引
    __table_args__ = (
        Index('idx_interaction_customer_id', 'customer_id'),
        Index('idx_interaction_type', 'interaction_type'),
        Index('idx_interaction_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<Interaction(id={self.id}, customer_id={self.customer_id}, type={self.interaction_type})>"


class AIAnalysis(Base):
    """AI 對話分析結果"""
    __tablename__ = "ai_analyses"

    # 主鍵
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 外鍵
    interaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("interactions.id", ondelete="CASCADE"))
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"))

    # 分析結果
    matched_questions: Mapped[dict] = mapped_column(JSON)  # 匹配的業務30問
    summary: Mapped[Optional[str]] = mapped_column(Text)  # 對話摘要
    coverage_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))  # 覆蓋率 (0-100)
    quality_score: Mapped[Optional[int]] = mapped_column(Integer)  # 品質評分 (0-100)

    # 客戶資訊提取
    extracted_info: Mapped[Optional[dict]] = mapped_column(JSON)

    # AA 客戶評估
    is_aa_customer: Mapped[Optional[bool]] = mapped_column(Boolean)
    aa_confidence: Mapped[Optional[int]] = mapped_column(Integer)  # 0-100
    aa_reasons: Mapped[Optional[list]] = mapped_column(JSON)  # AA 判定原因
    aa_score: Mapped[Optional[int]] = mapped_column(Integer)  # 0-100

    # AI 模型資訊
    ai_model_version: Mapped[Optional[str]] = mapped_column(String(50))

    # 時間戳
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # 關聯
    interaction: Mapped["Interaction"] = relationship(back_populates="ai_analysis")
    customer: Mapped["Customer"] = relationship()

    # 索引
    __table_args__ = (
        Index('idx_ai_analysis_customer_id', 'customer_id'),
        Index('idx_ai_analysis_is_aa', 'is_aa_customer'),
    )

    def __repr__(self):
        return f"<AIAnalysis(id={self.id}, customer_id={self.customer_id}, is_aa={self.is_aa_customer})>"


class CustomerEvaluation(Base):
    """客戶評估歷史記錄"""
    __tablename__ = "customer_evaluations"

    # 主鍵
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 外鍵
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"))
    ai_analysis_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("ai_analyses.id", ondelete="SET NULL"))

    # 評估結果
    grade: Mapped[CustomerGrade] = mapped_column(Enum(CustomerGrade))
    score: Mapped[int] = mapped_column(Integer)  # 0-100
    evaluation_data: Mapped[dict] = mapped_column(JSON)  # 完整評估資料

    # 評估規則版本
    criteria_version: Mapped[Optional[str]] = mapped_column(String(50))

    # 備註
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # 時間戳
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    # 關聯
    customer: Mapped["Customer"] = relationship()
    creator: Mapped[Optional["User"]] = relationship()

    # 索引
    __table_args__ = (
        Index('idx_evaluation_customer_id', 'customer_id'),
        Index('idx_evaluation_grade', 'grade'),
        Index('idx_evaluation_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<CustomerEvaluation(id={self.id}, customer_id={self.customer_id}, grade={self.grade}, score={self.score})>"


class HealthCheckReport(Base):
    """客戶健檢報告"""
    __tablename__ = "health_check_reports"

    # 主鍵
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 外鍵
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"))
    evaluation_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("customer_evaluations.id", ondelete="SET NULL"))

    # 報告資訊
    report_title: Mapped[str] = mapped_column(String(255))
    report_content: Mapped[dict] = mapped_column(JSON)  # 完整報告資料（JSON 格式）

    # 檔案資訊
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    file_format: Mapped[str] = mapped_column(String(10))  # xlsx, pdf

    # 時間戳
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    # 關聯
    customer: Mapped["Customer"] = relationship()
    evaluation: Mapped[Optional["CustomerEvaluation"]] = relationship()
    creator: Mapped[Optional["User"]] = relationship()

    # 索引
    __table_args__ = (
        Index('idx_report_customer_id', 'customer_id'),
        Index('idx_report_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<HealthCheckReport(id={self.id}, customer_id={self.customer_id}, format={self.file_format})>"


# ================================
# 系統設定與參考資料
# ================================

class QuestionTemplate(Base):
    """客戶健檢問卷範本（可自訂問題）"""
    __tablename__ = "question_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category: Mapped[QuestionCategory] = mapped_column(Enum(QuestionCategory))
    visit_type: Mapped[VisitType] = mapped_column(Enum(VisitType))
    priority: Mapped[QuestionPriority] = mapped_column(Enum(QuestionPriority))
    order_index: Mapped[int] = mapped_column(Integer)

    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType))
    options: Mapped[Optional[dict]] = mapped_column(JSON)  # 選項（如果是選擇題）
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)

    # 評分權重（用於計算成熟度評分）
    score_weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 索引
    __table_args__ = (
        Index('idx_category_visit_type', 'category', 'visit_type'),
    )

    def __repr__(self):
        return f"<QuestionTemplate(id={self.id}, category={self.category}, question_text={self.question_text[:30]})>"


class AaCustomerCriteria(Base):
    """AA 客戶判定條件（可設定）"""
    __tablename__ = "aa_customer_criteria"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    condition_json: Mapped[dict] = mapped_column(JSON, nullable=False)  # 判定條件的 JSON 邏輯
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AaCustomerCriteria(id={self.id}, name={self.name}, is_active={self.is_active})>"
