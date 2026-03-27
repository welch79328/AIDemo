# sales-lead-management - 技術設計文件

## 文件資訊
- **功能名稱**: sales-lead-management (銷售潛在客戶管理)
- **版本**: 1.0.0
- **設計日期**: 2026-03-26
- **狀態**: 設計已生成，待審核
- **語言**: 繁體中文

---

## 1. 系統架構概覽

### 1.1 整體架構

本系統為現有「業務行動成效評估系統」的功能擴展，採用**混合方法 (Hybrid Approach)**：
- **重用**現有架構：資料庫連接、API 路由結構、前端框架、AI 服務
- **新增**專用模組：Excel 導入、檔案管理、互動記錄、報告生成
- **擴展**現有模型：Customer 表新增欄位

```
┌─────────────────────────────────────────────────────────────┐
│                         前端層 (Vue 3)                         │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐           │
│  │ 客戶管理   │  │  資料導入   │  │  健檢報告    │           │
│  │ (擴展)     │  │  (新增)     │  │  (新增)      │           │
│  └────────────┘  └─────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────┘
                           │ HTTPS/JSON
┌─────────────────────────────────────────────────────────────┐
│                      API 層 (FastAPI)                         │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐           │
│  │ /customers │  │  /leads     │  │  /reports    │           │
│  │ (擴展)     │  │  (新增)     │  │  (新增)      │           │
│  └────────────┘  └─────────────┘  └──────────────┘           │
│  ┌────────────────────────────────────────────────┐           │
│  │  /ai (AI 分析 - 已存在，僅擴展音訊轉文字)     │           │
│  └────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                     服務層 (Services)                         │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐           │
│  │ ExcelSvc   │  │  FileSvc    │  │  ReportSvc   │           │
│  │ (新增)     │  │  (新增)     │  │  (新增)      │           │
│  └────────────┘  └─────────────┘  └──────────────┘           │
│  ┌────────────────────────────────────────────────┐           │
│  │  OpenAISvc (已存在 + 新增 transcribe_audio)   │           │
│  └────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                  資料層 (PostgreSQL)                          │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐           │
│  │ customers  │  │ interactions│  │  import_     │           │
│  │ (擴展)     │  │  (新增)     │  │  batches     │           │
│  └────────────┘  └─────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                      外部服務                                 │
│  OpenAI Whisper API  │  Email Service  │  File Storage       │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 核心組件及職責

| 組件 | 職責 | 狀態 |
|------|------|------|
| **ExcelService** | Excel 解析與生成 | 新增 |
| **FileService** | 檔案上傳、儲存、檢索 | 新增 |
| **ReportService** | 健檢報告生成（Excel/PDF） | 新增 |
| **OpenAIService** | AI 對話分析、音訊轉文字 | 擴展 |
| **Customer API** | 客戶資料 CRUD | 擴展 |
| **Interaction API** | 互動記錄管理 | 新增 |
| **Lead Import API** | Excel 名單導入 | 新增 |
| **Report API** | 報告管理與匯出 | 新增 |

### 1.3 與現有系統的集成點

1. **資料模型集成**
   - 擴展 `Customer` 模型（新增 `ad_source`, `import_batch_id`）
   - 重用 `is_aa_customer`, `maturity_score` 欄位
   - 保持與 `Visit`, `Contract` 的關聯一致性

2. **AI 服務集成**
   - ✅ 重用 `analyze_conversation()` - 業務30問匹配
   - ✅ 重用 `assess_aa_customer()` - AA 客戶評估
   - ⭐ 新增 `transcribe_audio()` - 音訊轉文字

3. **前端集成**
   - 重用 Element Plus 組件庫
   - 重用 Pinia 狀態管理模式
   - 重用 Axios HTTP 客戶端配置
   - 重用 ECharts 圖表庫

---

## 2. 資料模型設計

### 2.1 新增資料表

#### Table: `interactions` (互動記錄)

**用途**: 記錄銷售人員與客戶的所有互動（文檔、錄音、狀態變更）

```python
class Interaction(Base):
    __tablename__ = "interactions"

    # 主鍵
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 外鍵
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"))

    # 互動類型與內容
    interaction_type: Mapped[InteractionType] = mapped_column(Enum(InteractionType))  # document, audio, status_change
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
```

**Enum 定義**:
```python
class InteractionType(str, PyEnum):
    DOCUMENT = "document"        # 文檔上傳
    AUDIO = "audio"              # 錄音檔
    STATUS_CHANGE = "status_change"  # 狀態變更記錄
```

---

#### Table: `ai_analyses` (AI 分析結果)

**用途**: 儲存對話分析、業務30問匹配、AA評估結果

```python
class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    # 主鍵
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 外鍵
    interaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("interactions.id", ondelete="CASCADE"))
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"))

    # 分析結果
    matched_questions: Mapped[dict] = mapped_column(JSON)  # 匹配的業務30問
    """
    格式: [
        {
            "question_number": 1,
            "question_text": "問題內容",
            "answer": "客戶回答",
            "confidence": 85,
            "evidence": "對話片段"
        }
    ]
    """

    summary: Mapped[Optional[str]] = mapped_column(Text)  # 對話摘要
    coverage_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))  # 覆蓋率 (0-100)
    quality_score: Mapped[Optional[int]] = mapped_column(Integer)  # 品質評分 (0-100)

    # 客戶資訊提取
    extracted_info: Mapped[Optional[dict]] = mapped_column(JSON)
    """
    格式: {
        "company_name": "公司名稱",
        "property_count": 100,
        "staff_count": 5,
        "business_type": "包租",
        "pain_points": ["痛點1", "痛點2"]
    }
    """

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
```

---

#### Table: `customer_evaluations` (客戶評估歷史)

**用途**: 追蹤客戶評估歷史和等級變更

```python
class CustomerEvaluation(Base):
    __tablename__ = "customer_evaluations"

    # 主鍵
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 外鍵
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"))
    ai_analysis_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("ai_analyses.id", ondelete="SET NULL"))

    # 評估結果
    grade: Mapped[CustomerGrade] = mapped_column(Enum(CustomerGrade))  # AA, A, B, C
    score: Mapped[int] = mapped_column(Integer)  # 0-100
    evaluation_data: Mapped[dict] = mapped_column(JSON)  # 完整評估資料

    # 評估規則版本（用於追蹤規則變更）
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
```

**Enum 定義**:
```python
class CustomerGrade(str, PyEnum):
    AA = "AA"  # 高價值客戶
    A = "A"    # 優質客戶
    B = "B"    # 一般客戶
    C = "C"    # 低價值客戶
```

---

#### Table: `health_check_reports` (健檢報告)

**用途**: 儲存生成的客戶健檢報告

```python
class HealthCheckReport(Base):
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
    file_path: Mapped[Optional[str]] = mapped_column(String(500))  # Excel/PDF 檔案路徑
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
```

---

#### Table: `import_batches` (導入批次)

**用途**: 記錄每次 Excel 導入操作

```python
class ImportBatch(Base):
    __tablename__ = "import_batches"

    # 主鍵
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 檔案資訊
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[Optional[str]] = mapped_column(String(500))

    # 導入結果
    status: Mapped[ImportStatus] = mapped_column(Enum(ImportStatus))  # processing, completed, failed
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    fail_count: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_count: Mapped[int] = mapped_column(Integer, default=0)

    # 錯誤記錄
    error_log: Mapped[Optional[dict]] = mapped_column(JSON)  # 錯誤詳情

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
```

**Enum 定義**:
```python
class ImportStatus(str, PyEnum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

---

### 2.2 修改現有資料表

#### Table: `customers` (客戶) - 擴展

**新增欄位**:

```python
class Customer(Base):
    # ... 現有欄位保持不變 ...

    # ============ 新增欄位 ============

    # 廣告來源
    ad_source: Mapped[Optional[str]] = mapped_column(String(100))  # e.g. "3特點輪播廣告"

    # 導入批次
    import_batch_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("import_batches.id", ondelete="SET NULL"))

    # ============ 新增關聯 ============

    import_batch: Mapped[Optional["ImportBatch"]] = relationship(back_populates="customers")
    interactions: Mapped[list["Interaction"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
    evaluations: Mapped[list["CustomerEvaluation"]] = relationship(cascade="all, delete-orphan")
    reports: Mapped[list["HealthCheckReport"]] = relationship(cascade="all, delete-orphan")
```

**新增索引**:
```python
__table_args__ = (
    # ... 現有索引 ...
    Index('idx_ad_source', 'ad_source'),
    Index('idx_import_batch_id', 'import_batch_id'),
)
```

---

### 2.3 資料關係圖（ER 圖）

```
┌──────────────────┐
│   ImportBatch    │
│  (導入批次)       │
└────────┬─────────┘
         │ 1
         │
         │ N
┌────────▼─────────┐        N  ┌──────────────────┐
│    Customer      │◄──────────┤   Interaction    │
│    (客戶)        │            │   (互動記錄)      │
└────────┬─────────┘            └────────┬─────────┘
         │                               │ 1
         │ 1                             │
         │                               │ 1
         │ N                      ┌──────▼─────────┐
    ┌────▼──────────────┐         │   AIAnalysis   │
    │ CustomerEvaluation│         │  (AI分析結果)   │
    │  (客戶評估歷史)    │         └────────────────┘
    └───────────────────┘
         │ 1
         │
         │ N
    ┌────▼──────────────┐
    │ HealthCheckReport │
    │   (健檢報告)       │
    └───────────────────┘

關聯說明：
1. ImportBatch → Customer (1:N): 一個批次可導入多個客戶
2. Customer → Interaction (1:N): 一個客戶有多筆互動記錄
3. Interaction → AIAnalysis (1:1): 一筆互動對應一份分析結果
4. Customer → CustomerEvaluation (1:N): 一個客戶有多次評估歷史
5. CustomerEvaluation → HealthCheckReport (1:N): 一次評估可生成多份報告
```

---

## 3. API 設計

### 3.1 新增 API 端點

#### 3.1.1 Excel 導入 API

##### POST `/api/v1/leads/import`

**功能**: 上傳並解析 Excel 檔案，導入潛在客戶名單

**請求**:
```python
# Request (multipart/form-data)
class LeadImportRequest:
    file: UploadFile  # Excel 檔案
    options: Optional[ImportOptions] = None  # 導入選項

class ImportOptions(BaseModel):
    skip_duplicates: bool = False  # 跳過重複資料
    update_existing: bool = False  # 更新現有資料
    dry_run: bool = False  # 乾運行（不實際導入）
```

**回應**:
```python
class LeadImportResponse(BaseModel):
    batch_id: str  # 導入批次 ID
    status: str  # processing, completed, failed
    total_rows: int
    success_count: int
    fail_count: int
    duplicate_count: int
    duplicates: List[DuplicateInfo]  # 重複資料詳情
    errors: List[ImportError]  # 錯誤詳情

class DuplicateInfo(BaseModel):
    row_number: int
    customer_name: str
    phone: str
    existing_customer_id: str

class ImportError(BaseModel):
    row_number: int
    error_type: str
    error_message: str
    row_data: Dict[str, Any]
```

**錯誤處理**:
- 400: 檔案格式錯誤
- 413: 檔案過大 (> 10MB)
- 422: 資料驗證失敗

---

##### GET `/api/v1/leads/import/history`

**功能**: 查詢導入歷史記錄

**請求**:
```python
# Query Parameters
page: int = 1
limit: int = 20
status: Optional[ImportStatus] = None
```

**回應**:
```python
class ImportHistoryResponse(BaseModel):
    batches: List[ImportBatchSummary]
    total: int
    page: int
    limit: int
    total_pages: int

class ImportBatchSummary(BaseModel):
    id: str
    file_name: str
    status: str
    total_rows: int
    success_count: int
    fail_count: int
    created_at: datetime
    created_by: Optional[str]
```

---

#### 3.1.2 互動記錄 API

##### POST `/api/v1/interactions`

**功能**: 創建互動記錄（非檔案上傳）

**請求**:
```python
class InteractionCreate(BaseModel):
    customer_id: str
    interaction_type: InteractionType
    title: Optional[str] = None
    notes: Optional[str] = None
```

**回應**:
```python
class InteractionResponse(BaseModel):
    id: str
    customer_id: str
    interaction_type: str
    title: Optional[str]
    notes: Optional[str]
    created_at: datetime
    created_by: Optional[str]
```

---

##### POST `/api/v1/interactions/upload`

**功能**: 上傳檔案並創建互動記錄

**請求**:
```python
# Request (multipart/form-data)
customer_id: str
interaction_type: str  # document, audio
title: Optional[str]
notes: Optional[str]
file: UploadFile
```

**回應**:
```python
class InteractionUploadResponse(BaseModel):
    id: str
    customer_id: str
    interaction_type: str
    file_name: str
    file_size: int
    file_type: str
    audio_duration: Optional[int]  # 僅音訊檔
    created_at: datetime
```

**檔案驗證**:
- **文檔**: .doc, .docx, .pdf, .jpg, .png (最大 10MB)
- **音訊**: .mp3, .wav, .m4a (最大 50MB)

---

##### GET `/api/v1/interactions`

**功能**: 查詢互動記錄列表

**請求**:
```python
# Query Parameters
customer_id: Optional[str] = None
interaction_type: Optional[InteractionType] = None
page: int = 1
limit: int = 20
```

**回應**:
```python
class InteractionListResponse(BaseModel):
    interactions: List[InteractionResponse]
    total: int
    page: int
    limit: int
```

---

#### 3.1.3 AI 服務 API（新增）

##### POST `/api/v1/ai/transcribe`

**功能**: 將音訊檔轉換為文字稿

**請求**:
```python
class AudioTranscribeRequest(BaseModel):
    interaction_id: str  # 互動記錄 ID（包含音訊檔）
    language: str = "zh"  # 語言代碼
```

**回應**:
```python
class AudioTranscribeResponse(BaseModel):
    interaction_id: str
    transcript_text: str  # 轉換後的文字稿
    audio_duration: int  # 音訊時長（秒）
    processing_time: float  # 處理時間（秒）
    model_version: str
```

**錯誤處理**:
- 400: 互動記錄不包含音訊檔
- 500: AI 服務調用失敗
- 503: AI 服務暫時不可用

---

#### 3.1.4 報告生成 API

##### POST `/api/v1/reports/generate`

**功能**: 生成客戶健檢報告

**請求**:
```python
class ReportGenerateRequest(BaseModel):
    customer_id: str
    evaluation_id: Optional[str] = None  # 指定評估記錄，否則使用最新
    format: str = "xlsx"  # xlsx, pdf
    include_ai_analysis: bool = True
```

**回應**:
```python
class ReportGenerateResponse(BaseModel):
    report_id: str
    customer_id: str
    file_path: str
    file_format: str
    created_at: datetime
```

---

##### GET `/api/v1/reports/{report_id}/export`

**功能**: 下載報告檔案

**請求**: 路徑參數 `report_id`

**回應**:
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (Excel)
- Content-Type: `application/pdf` (PDF)
- Content-Disposition: `attachment; filename="客戶名_健檢報告_日期.xlsx"`

---

##### POST `/api/v1/reports/batch-export`

**功能**: 批次匯出多個客戶報告（ZIP）

**請求**:
```python
class BatchExportRequest(BaseModel):
    customer_ids: List[str]  # 客戶 ID 列表
    format: str = "xlsx"
```

**回應**:
- Content-Type: `application/zip`
- Content-Disposition: `attachment; filename="健檢報告_批次匯出_日期.zip"`

---

##### POST `/api/v1/reports/send-email`

**功能**: 透過 Email 分享報告

**請求**:
```python
class ReportEmailRequest(BaseModel):
    report_id: str
    recipient_email: str
    subject: Optional[str] = None
    message: Optional[str] = None
```

**回應**:
```python
class ReportEmailResponse(BaseModel):
    success: bool
    message: str
    sent_at: datetime
```

---

### 3.2 現有 API 復用

以下 API 已完整實作，**無需修改，直接使用**：

#### AI 分析 API（已存在）

##### POST `/api/v1/ai/analyze-conversation`
- **功能**: 分析對話並匹配業務30問
- **已實作**: ✅ 完整實作
- **檔案**: `backend/app/api/v1/ai_analysis.py:27-63`

##### POST `/api/v1/ai/extract-customer-info`
- **功能**: 提取客戶基本資訊
- **已實作**: ✅ 完整實作
- **檔案**: `backend/app/api/v1/ai_analysis.py:66-87`

##### POST `/api/v1/ai/assess-aa-customer`
- **功能**: 評估 AA 客戶
- **已實作**: ✅ 完整實作
- **檔案**: `backend/app/api/v1/ai_analysis.py:90-118`

##### GET `/api/v1/ai/questionnaire`
- **功能**: 獲取業務30問題庫
- **已實作**: ✅ 完整實作
- **檔案**: `backend/app/api/v1/ai_analysis.py:121-133`

#### 客戶管理 API（需擴展）

##### GET `/api/v1/customers`
- **功能**: 客戶列表（支援搜尋、篩選、分頁）
- **需擴展**: 新增 `ad_source`, `import_batch_id` 篩選參數

##### PATCH `/api/v1/customers/{customer_id}`
- **功能**: 更新客戶資料
- **需擴展**: 支援更新新增欄位

---

## 4. 服務層設計

### 4.1 新增服務

#### 4.1.1 ExcelService (Excel 處理服務)

**檔案**: `backend/app/services/excel_service.py`

**職責**:
- Excel 檔案解析（導入）
- Excel 報告生成（匯出）
- 資料驗證和格式轉換

**核心方法**:

```python
from typing import List, Dict, Any, Tuple
from pathlib import Path
import openpyxl
import pandas as pd

class ExcelService:
    """Excel 處理服務"""

    async def parse_lead_import_file(
        self,
        file_path: Path
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        解析導入的 Excel 檔案

        Returns:
            (valid_rows, error_rows) - 有效資料和錯誤資料
        """
        pass

    async def detect_duplicates(
        self,
        db: AsyncSession,
        rows: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """檢測重複資料（比對電話、Email）"""
        pass

    async def generate_health_check_report(
        self,
        customer: Customer,
        evaluation: CustomerEvaluation,
        ai_analysis: Optional[AIAnalysis],
        template_path: Optional[Path] = None
    ) -> Path:
        """
        生成客戶健檢報告 Excel 檔案

        Returns:
            生成的檔案路徑
        """
        pass

    async def generate_import_error_report(
        self,
        errors: List[ImportError]
    ) -> Path:
        """生成導入錯誤報告"""
        pass
```

**依賴套件**:
- `openpyxl` (已安裝): Excel 讀寫
- `pandas` (已安裝): 資料處理

---

#### 4.1.2 FileService (檔案管理服務)

**檔案**: `backend/app/services/file_service.py`

**職責**:
- 檔案上傳處理
- 檔案儲存（本地/S3）
- 檔案檢索和刪除
- 檔案驗證（類型、大小）

**核心方法**:

```python
from fastapi import UploadFile
from pathlib import Path
from typing import Optional, Tuple
from enum import Enum

class StorageBackend(str, Enum):
    LOCAL = "local"
    S3 = "s3"

class FileService:
    """檔案管理服務"""

    def __init__(self, backend: StorageBackend = StorageBackend.LOCAL):
        self.backend = backend
        self.storage = self._init_storage(backend)

    async def upload_file(
        self,
        file: UploadFile,
        folder: str,  # e.g. "interactions", "imports", "reports"
        allowed_extensions: Optional[List[str]] = None,
        max_size: Optional[int] = None  # bytes
    ) -> Tuple[str, Dict[str, Any]]:
        """
        上傳檔案

        Returns:
            (file_path, metadata) - 檔案路徑和元數據
        """
        pass

    async def get_file_path(
        self,
        file_path: str
    ) -> Path:
        """獲取檔案實際路徑（用於讀取）"""
        pass

    async def delete_file(
        self,
        file_path: str
    ) -> bool:
        """刪除檔案"""
        pass

    async def extract_audio_metadata(
        self,
        file_path: Path
    ) -> Dict[str, Any]:
        """
        提取音訊檔元數據

        Returns:
            {
                "duration": 300,  # 秒
                "format": "mp3",
                "bitrate": 128000
            }
        """
        pass

    def _init_storage(self, backend: StorageBackend):
        """初始化儲存後端"""
        if backend == StorageBackend.LOCAL:
            return LocalStorage()
        elif backend == StorageBackend.S3:
            return S3Storage()
```

**儲存抽象介面**:

```python
from abc import ABC, abstractmethod

class StorageBackend(ABC):
    """儲存後端抽象類"""

    @abstractmethod
    async def save(self, file: UploadFile, path: str) -> str:
        """儲存檔案"""
        pass

    @abstractmethod
    async def get(self, path: str) -> Path:
        """獲取檔案"""
        pass

    @abstractmethod
    async def delete(self, path: str) -> bool:
        """刪除檔案"""
        pass

class LocalStorage(StorageBackend):
    """本地檔案系統儲存（MVP）"""

    def __init__(self):
        self.base_path = Path("./storage")
        self.base_path.mkdir(exist_ok=True)

class S3Storage(StorageBackend):
    """S3 相容儲存（生產環境）"""

    def __init__(self):
        # Initialize S3 client (boto3)
        pass
```

**依賴套件**:
- `mutagen` (需安裝): 音訊元數據提取
- `boto3` (可選): S3 整合

---

#### 4.1.3 ReportService (報告生成服務)

**檔案**: `backend/app/services/report_service.py`

**職責**:
- 健檢報告生成（Excel/PDF）
- 報告資料聚合
- 報告範本管理

**核心方法**:

```python
from typing import Optional
from pathlib import Path

class ReportService:
    """報告生成服務"""

    def __init__(
        self,
        excel_service: ExcelService,
        file_service: FileService
    ):
        self.excel_service = excel_service
        self.file_service = file_service

    async def generate_health_check_report(
        self,
        db: AsyncSession,
        customer_id: str,
        evaluation_id: Optional[str] = None,
        format: str = "xlsx"
    ) -> HealthCheckReport:
        """
        生成健檢報告

        流程:
        1. 獲取客戶資料
        2. 獲取評估記錄（最新或指定）
        3. 獲取 AI 分析結果
        4. 生成報告檔案（Excel 或 PDF）
        5. 儲存報告記錄
        """
        pass

    async def generate_batch_reports(
        self,
        db: AsyncSession,
        customer_ids: List[str],
        format: str = "xlsx"
    ) -> Path:
        """
        批次生成報告並打包為 ZIP

        Returns:
            ZIP 檔案路徑
        """
        pass

    async def send_report_email(
        self,
        db: AsyncSession,
        report_id: str,
        recipient_email: str,
        subject: Optional[str] = None,
        message: Optional[str] = None
    ) -> bool:
        """透過 Email 發送報告"""
        pass
```

**依賴套件**:
- `WeasyPrint` (需安裝): PDF 生成
- SMTP 或 Email 服務 API

---

### 4.2 擴展現有服務

#### OpenAIService (擴展)

**檔案**: `backend/app/services/openai_service.py`

**新增方法**:

```python
class OpenAIService:
    # ... 現有方法保持不變 ...

    async def transcribe_audio(
        self,
        audio_file_path: Path,
        language: str = "zh"
    ) -> Dict[str, Any]:
        """
        使用 Whisper API 將音訊轉為文字

        Args:
            audio_file_path: 音訊檔案路徑
            language: 語言代碼（zh 為中文）

        Returns:
            {
                "text": "轉換後的文字稿",
                "duration": 300,  # 音訊時長（秒）
                "model": "whisper-1"
            }
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="text"
                )

            return {
                "text": transcript,
                "model": "whisper-1"
            }

        except Exception as e:
            print(f"Whisper API 錯誤: {str(e)}")
            raise
```

**現有方法（無需修改）**:
- ✅ `analyze_conversation()` - 對話分析
- ✅ `extract_customer_info()` - 資訊提取
- ✅ `assess_aa_customer()` - AA 評估

---

## 5. 前端組件設計

### 5.1 新增頁面

#### 5.1.1 資料導入頁 (`/leads/import`)

**檔案**: `frontend/src/views/Leads/Import.vue`

**功能**:
- 上傳 Excel 檔案
- 顯示解析進度
- 處理重複資料選擇
- 顯示導入結果摘要
- 下載錯誤報告

**組件結構**:
```vue
<template>
  <div class="lead-import-page">
    <el-card>
      <template #header>
        <h2>潛在客戶名單導入</h2>
      </template>

      <!-- 檔案上傳區 -->
      <FileUpload
        accept=".xlsx,.xls"
        :max-size="10 * 1024 * 1024"
        @upload="handleUpload"
      />

      <!-- 導入進度 -->
      <ImportProgress v-if="importing" :progress="importProgress" />

      <!-- 重複資料處理 -->
      <DuplicateHandler
        v-if="duplicates.length > 0"
        :duplicates="duplicates"
        @resolve="handleDuplicateResolve"
      />

      <!-- 導入結果 -->
      <ImportResult v-if="importResult" :result="importResult" />
    </el-card>

    <!-- 導入歷史 -->
    <ImportHistory />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { importLeads, getImportHistory } from '@/api/lead'

const importing = ref(false)
const importProgress = ref(0)
const duplicates = ref([])
const importResult = ref(null)

async function handleUpload(file: File) {
  importing.value = true
  // 上傳並處理...
}
</script>
```

---

#### 5.1.2 系統設定頁 (`/settings`)

**檔案**: `frontend/src/views/Settings/Index.vue`

**功能**:
- 客戶分級規則配置
- 業務30問權重設定
- AA 客戶判定標準設定

**組件結構**:
```vue
<template>
  <div class="settings-page">
    <el-tabs v-model="activeTab">
      <!-- 分級規則 -->
      <el-tab-pane label="客戶分級規則" name="grading">
        <GradingRulesConfig />
      </el-tab-pane>

      <!-- 業務30問 -->
      <el-tab-pane label="業務30問設定" name="questions">
        <QuestionWeightConfig />
      </el-tab-pane>

      <!-- AA 客戶標準 -->
      <el-tab-pane label="AA 客戶標準" name="aa-criteria">
        <AACriteriaConfig />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
```

---

### 5.2 修改現有頁面

#### 5.2.1 客戶列表頁 (`/customers`)

**檔案**: `frontend/src/views/Customers/Index.vue`

**新增功能**:
- 新增「廣告來源」篩選條件
- 新增「導入批次」篩選條件
- 新增「匯入日期」欄位顯示

**修改**:
```vue
<template>
  <!-- 篩選條件 -->
  <el-form inline>
    <!-- 現有篩選... -->

    <!-- 新增：廣告來源篩選 -->
    <el-form-item label="廣告來源">
      <el-select v-model="filters.adSource">
        <el-option label="全部" value="" />
        <el-option label="3特點輪播廣告" value="3特點輪播廣告" />
        <!-- 其他來源... -->
      </el-select>
    </el-form-item>

    <!-- 新增：導入批次篩選 -->
    <el-form-item label="導入批次">
      <el-select v-model="filters.importBatchId">
        <!-- 批次選項... -->
      </el-select>
    </el-form-item>
  </el-form>
</template>
```

---

#### 5.2.2 客戶詳情頁 (`/customers/:id`)

**檔案**: `frontend/src/views/Customers/Detail.vue`

**新增功能**:
- 互動記錄時間軸
- 健檢報告區域
- 檔案上傳功能

**修改**:
```vue
<template>
  <div class="customer-detail-page">
    <!-- 現有：基本資料卡 -->
    <CustomerInfoCard :customer="customer" />

    <!-- 新增：互動記錄時間軸 -->
    <el-card>
      <template #header>互動記錄</template>
      <InteractionTimeline :customer-id="customerId" />
      <FileUploadSection @uploaded="refreshTimeline" />
    </el-card>

    <!-- 新增：健檢報告區 -->
    <el-card>
      <template #header>客戶健檢報告</template>
      <HealthCheckReportSection :customer-id="customerId" />
    </el-card>
  </div>
</template>
```

---

### 5.3 新增組件

#### 5.3.1 FileUpload.vue (檔案上傳組件)

**檔案**: `frontend/src/components/FileUpload.vue`

**Props**:
```typescript
interface FileUploadProps {
  accept?: string  // 接受的檔案類型，如 ".xlsx,.xls"
  maxSize?: number  // 最大檔案大小（bytes）
  multiple?: boolean  // 是否允許多檔案
}

interface FileUploadEmits {
  (e: 'upload', file: File): void
  (e: 'error', error: Error): void
}
```

**功能**:
- 拖放上傳
- 檔案類型驗證
- 檔案大小驗證
- 上傳進度顯示

---

#### 5.3.2 AudioPlayer.vue (音訊播放器)

**檔案**: `frontend/src/components/AudioPlayer.vue`

**Props**:
```typescript
interface AudioPlayerProps {
  src: string  // 音訊檔案 URL
  duration?: number  // 音訊時長（秒）
}
```

**功能**:
- 播放/暫停
- 進度條
- 時間顯示
- 播放速度調整

---

#### 5.3.3 Timeline.vue (互動時間軸)

**檔案**: `frontend/src/components/Timeline.vue`

**Props**:
```typescript
interface TimelineProps {
  customerId: string
  filter?: 'all' | 'document' | 'audio' | 'status_change'
}

interface TimelineItem {
  id: string
  type: 'document' | 'audio' | 'status_change'
  title: string
  content: string
  timestamp: Date
  fileUrl?: string
  audioUrl?: string
}
```

**功能**:
- 時間倒序排列
- 篩選互動類型
- 檔案預覽/下載
- 音訊播放

---

#### 5.3.4 ReportPreview.vue (報告預覽)

**檔案**: `frontend/src/components/ReportPreview.vue`

**Props**:
```typescript
interface ReportPreviewProps {
  reportId: string
}
```

**功能**:
- HTML 格式預覽
- 下載按鈕（Excel/PDF）
- Email 分享功能
- 列印按鈕

---

## 6. 檔案儲存策略

### 6.1 本地儲存方案（MVP）

**目錄結構**:
```
storage/
├── imports/          # Excel 導入檔案
│   └── YYYY-MM-DD/
│       └── {batch_id}_{filename}.xlsx
├── interactions/     # 互動檔案
│   └── documents/    # 文檔
│   └── audio/        # 錄音檔
├── reports/          # 健檢報告
│   └── YYYY-MM-DD/
│       └── {customer_id}_{timestamp}.xlsx
└── temp/             # 臨時檔案
```

**配置**:
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # ... 現有配置 ...

    # 檔案儲存
    STORAGE_BACKEND: str = "local"  # local, s3
    LOCAL_STORAGE_PATH: Path = Path("./storage")

    # 檔案限制
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_DOCUMENT_TYPES: List[str] = [".doc", ".docx", ".pdf", ".jpg", ".png"]
    ALLOWED_AUDIO_TYPES: List[str] = [".mp3", ".wav", ".m4a"]
```

### 6.2 S3 相容儲存方案（生產環境）

**配置**:
```python
class Settings(BaseSettings):
    # S3 配置
    S3_ENDPOINT: Optional[str] = None  # MinIO / AWS S3
    S3_BUCKET_NAME: str = "sales-lead-management"
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_REGION: str = "us-east-1"
```

**Bucket 結構**:
```
bucket: sales-lead-management
├── imports/{batch_id}/{filename}
├── interactions/documents/{customer_id}/{file_id}
├── interactions/audio/{customer_id}/{file_id}
└── reports/{customer_id}/{report_id}
```

---

## 7. 外部依賴整合

### 7.1 OpenAI Whisper API

**文件**: https://platform.openai.com/docs/guides/speech-to-text

**整合方式**:
- 使用現有 `openai` 套件 (已安裝 v1.12.0)
- 新增 `transcribe_audio()` 方法於 `OpenAIService`

**API 限制**:
- 最大檔案大小: 25MB
- 支援格式: mp3, mp4, mpeg, mpga, m4a, wav, webm
- 成本: $0.006 / 分鐘

**錯誤處理**:
```python
# 檔案過大處理：分段上傳
if file_size > 25 * 1024 * 1024:
    # 使用 pydub 分割音訊
    chunks = split_audio(file_path, chunk_duration=600)  # 10分鐘一段
    transcripts = []
    for chunk in chunks:
        transcript = await transcribe_audio(chunk)
        transcripts.append(transcript)
    return "\n".join(transcripts)
```

---

### 7.2 Email 服務

**選項 A: SMTP (MVP)**

**配置**:
```python
class Settings(BaseSettings):
    # Email SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@jgbsmart.com"
```

**實作**:
```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

async def send_report_email(
    recipient: str,
    subject: str,
    body: str,
    attachment_path: Path
):
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = recipient
    msg['Subject'] = subject

    # 附件
    with open(attachment_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={attachment_path.name}')
        msg.attach(part)

    # 發送
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
```

**選項 B: SendGrid (生產環境)**

**套件**: `sendgrid` (需安裝)

---

### 7.3 PDF 生成

**選項**: WeasyPrint

**安裝**:
```bash
pip install WeasyPrint
```

**實作**:
```python
from weasyprint import HTML, CSS
from pathlib import Path

async def generate_pdf_report(
    html_content: str,
    output_path: Path
):
    """從 HTML 生成 PDF"""
    HTML(string=html_content).write_pdf(
        output_path,
        stylesheets=[CSS(string="""
            @page { size: A4; margin: 2cm; }
            body { font-family: 'Microsoft YaHei', sans-serif; }
        """)]
    )
```

---

## 8. 安全設計

### 8.1 檔案上傳安全

**驗證措施**:

1. **檔案類型白名單**
```python
ALLOWED_MIME_TYPES = {
    'document': [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg',
        'image/png'
    ],
    'audio': [
        'audio/mpeg',
        'audio/wav',
        'audio/x-m4a'
    ]
}

def validate_file_type(file: UploadFile, category: str):
    if file.content_type not in ALLOWED_MIME_TYPES[category]:
        raise HTTPException(400, "不支援的檔案類型")
```

2. **檔案大小限制**
```python
MAX_FILE_SIZE = {
    'document': 10 * 1024 * 1024,  # 10MB
    'audio': 50 * 1024 * 1024,      # 50MB
    'excel': 10 * 1024 * 1024       # 10MB
}
```

3. **檔案名稱清理**
```python
import re
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    """清理檔案名稱，防止路徑穿越攻擊"""
    # 移除路徑分隔符
    filename = filename.replace('/', '').replace('\\', '')
    # 僅保留安全字符
    filename = re.sub(r'[^\w\s.-]', '', filename)
    return filename[:255]  # 限制長度
```

4. **病毒掃描（可選）**
```python
# 整合 ClamAV 或類似服務
async def scan_file(file_path: Path) -> bool:
    # 病毒掃描邏輯
    pass
```

### 8.2 敏感資料加密

**資料庫加密欄位**:
```python
from cryptography.fernet import Fernet

class Customer(Base):
    # 加密電話號碼
    _contact_phone: Mapped[Optional[bytes]] = mapped_column("contact_phone", LargeBinary, nullable=True)

    @hybrid_property
    def contact_phone(self) -> Optional[str]:
        if self._contact_phone:
            return cipher_suite.decrypt(self._contact_phone).decode()
        return None

    @contact_phone.setter
    def contact_phone(self, value: Optional[str]):
        if value:
            self._contact_phone = cipher_suite.encrypt(value.encode())
        else:
            self._contact_phone = None
```

### 8.3 API 安全

**速率限制**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/leads/import")
@limiter.limit("5/minute")  # 每分鐘最多 5 次
async def import_leads(...):
    pass
```

---

## 9. 效能考慮

### 9.1 大檔案上傳處理

**分塊上傳**:
```python
from fastapi import UploadFile
import aiofiles

async def save_upload_file_in_chunks(
    upload_file: UploadFile,
    destination: Path,
    chunk_size: int = 1024 * 1024  # 1MB
):
    async with aiofiles.open(destination, 'wb') as f:
        while chunk := await upload_file.read(chunk_size):
            await f.write(chunk)
```

### 9.2 Excel 批量導入優化

**批次處理**:
```python
async def import_customers_batch(
    db: AsyncSession,
    rows: List[Dict[str, Any]],
    batch_size: int = 100
):
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        # 批次插入
        db.bulk_insert_mappings(Customer, batch)
        await db.commit()
```

### 9.3 AI 服務調用快取

**Redis 快取**:
```python
from redis import asyncio as aioredis
import hashlib
import json

async def cached_ai_analysis(
    conversation_text: str,
    cache_ttl: int = 3600  # 1小時
) -> Dict:
    # 生成快取鍵
    cache_key = f"ai:analysis:{hashlib.md5(conversation_text.encode()).hexdigest()}"

    # 檢查快取
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # 調用 AI
    result = await openai_service.analyze_conversation(conversation_text, QUESTIONNAIRE_DATA)

    # 儲存快取
    await redis.setex(cache_key, cache_ttl, json.dumps(result))

    return result
```

---

## 10. 錯誤處理策略

### 10.1 檔案解析錯誤

```python
class FileParseError(Exception):
    def __init__(self, row_number: int, error_type: str, message: str):
        self.row_number = row_number
        self.error_type = error_type
        self.message = message

try:
    rows = parse_excel(file_path)
except FileParseError as e:
    # 記錄錯誤並繼續處理其他行
    errors.append({
        "row": e.row_number,
        "type": e.error_type,
        "message": e.message
    })
```

### 10.2 AI 服務調用失敗

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_openai_with_retry(prompt: str):
    try:
        return await openai_service.analyze_conversation(prompt, QUESTIONNAIRE_DATA)
    except Exception as e:
        logger.error(f"OpenAI API 調用失敗: {str(e)}")
        raise
```

### 10.3 重複資料處理

```python
class DuplicateHandlingStrategy(str, Enum):
    SKIP = "skip"        # 跳過重複
    UPDATE = "update"    # 更新現有
    CREATE_NEW = "create_new"  # 創建新記錄

async def handle_duplicates(
    db: AsyncSession,
    duplicates: List[Dict],
    strategy: DuplicateHandlingStrategy
):
    if strategy == DuplicateHandlingStrategy.SKIP:
        return []
    elif strategy == DuplicateHandlingStrategy.UPDATE:
        # 更新現有客戶
        for dup in duplicates:
            await customer_crud.update(db, dup['existing_id'], dup['new_data'])
    # ...
```

---

## 11. 測試策略

### 11.1 單元測試

**目標覆蓋率**: ≥ 70%

**關鍵測試**:

```python
# tests/services/test_excel_service.py
import pytest
from app.services.excel_service import ExcelService

@pytest.mark.asyncio
async def test_parse_lead_import_file():
    service = ExcelService()
    valid, errors = await service.parse_lead_import_file(Path("test_data.xlsx"))

    assert len(valid) > 0
    assert all('company_name' in row for row in valid)

@pytest.mark.asyncio
async def test_detect_duplicates(db_session):
    service = ExcelService()
    rows = [
        {"phone": "0912345678", "name": "測試公司1"},
        {"phone": "0912345678", "name": "測試公司2"},  # 重複
    ]
    duplicates = await service.detect_duplicates(db_session, rows)

    assert len(duplicates) == 1
```

### 11.2 整合測試

```python
# tests/api/test_lead_import.py
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_import_leads_api(client: AsyncClient):
    files = {"file": ("test.xlsx", open("test.xlsx", "rb"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

    response = await client.post("/api/v1/leads/import", files=files)

    assert response.status_code == 200
    data = response.json()
    assert "batch_id" in data
    assert data["success_count"] > 0
```

### 11.3 E2E 測試場景

1. **完整導入流程**
   - 上傳 Excel → 處理重複 → 確認導入 → 驗證資料庫

2. **AI 分析流程**
   - 上傳錄音 → 轉文字 → 分析對話 → 評估 AA → 生成報告

3. **報告生成流程**
   - 選擇客戶 → 生成報告 → 下載 Excel → Email 分享

---

## 12. 部署考慮

### 12.1 資料庫遷移

**Alembic 遷移腳本**:

```bash
# 生成遷移腳本
alembic revision --autogenerate -m "add sales lead management tables"

# 執行遷移
alembic upgrade head
```

**遷移檢查清單**:
- [ ] 新增 5 個資料表
- [ ] 擴展 Customer 表（2 個欄位）
- [ ] 建立外鍵關聯
- [ ] 建立索引
- [ ] 測試 rollback

### 12.2 環境變數配置

**.env 範例**:
```bash
# 資料庫
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname

# OpenAI
OPENAI_API_KEY=sk-...

# 檔案儲存
STORAGE_BACKEND=local  # or s3
LOCAL_STORAGE_PATH=./storage

# S3 (如果使用)
S3_ENDPOINT=https://s3.amazonaws.com
S3_BUCKET_NAME=sales-lead-management
S3_ACCESS_KEY=...
S3_SECRET_KEY=...

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
EMAIL_FROM=noreply@jgbsmart.com

# 檔案限制
MAX_UPLOAD_SIZE_MB=50
```

### 12.3 依賴安裝

**新增依賴** (`requirements.txt`):
```
# AI
openai==1.12.0  # 已安裝

# Excel 處理
openpyxl==3.1.2  # 已安裝
xlsxwriter==3.1.9  # 已安裝
pandas==2.1.4  # 已安裝

# 檔案處理
python-multipart==0.0.6  # 已安裝
mutagen==1.47.0  # 需安裝 - 音訊元數據

# PDF 生成
WeasyPrint==60.2  # 需安裝

# 重試機制
tenacity==8.2.3  # 已安裝

# S3 (可選)
boto3==1.34.0  # 需安裝（如果使用 S3）

# Email (可選)
sendgrid==6.11.0  # 需安裝（如果使用 SendGrid）
```

**安裝命令**:
```bash
pip install mutagen WeasyPrint
# 如需 S3: pip install boto3
# 如需 SendGrid: pip install sendgrid
```

---

## 13. 需求追溯表

| 需求 ID | 需求描述 | 對應設計組件 |
|---------|----------|--------------|
| 1.1 | Excel 名單導入 | ExcelService.parse_lead_import_file(), POST /api/v1/leads/import |
| 1.2 | 資料驗證與去重 | ExcelService.detect_duplicates() |
| 1.3 | 導入歷史記錄 | ImportBatch 模型, GET /api/v1/leads/import/history |
| 2.1 | 客戶資料檢視 | 擴展現有 GET /api/v1/customers（新增篩選參數） |
| 2.2 | 客戶資料編輯 | 擴展現有 PATCH /api/v1/customers/{id} |
| 2.3 | 聯絡狀態管理 | 擴展 Customer 模型, CustomerStatus Enum |
| 3.1 | 互動文檔上傳 | Interaction 模型, FileService, POST /api/v1/interactions/upload |
| 3.2 | 錄音檔上傳與管理 | FileService.extract_audio_metadata(), AudioPlayer.vue |
| 3.3 | 互動記錄時間軸 | Timeline.vue, GET /api/v1/interactions |
| 4.1 | 音訊轉文字 | OpenAIService.transcribe_audio(), POST /api/v1/ai/transcribe |
| 4.2 | 業務30問匹配分析 | ✅ 已實作: POST /api/v1/ai/analyze-conversation |
| 4.3 | 對話品質評估 | ✅ 已實作: AIAnalysis.coverage_rate, quality_score |
| 5.1 | AA 客戶識別 | ✅ 已實作: POST /api/v1/ai/assess-aa-customer |
| 5.2 | 客戶分級規則配置 | CustomerEvaluation 模型, GradingRulesConfig.vue |
| 5.3 | 評估結果追蹤 | CustomerEvaluation 模型, 評估歷史查詢 API |
| 6.1 | 客戶健檢紀錄表生成 | HealthCheckReport 模型, ReportService, ExcelService |
| 6.2 | 報告匯出功能 | POST /api/v1/reports/generate, GET /api/v1/reports/{id}/export |
| 6.3 | 報告檢視與列印 | ReportPreview.vue, WeasyPrint PDF 生成, Email 服務 |

---

## 附錄

### A. 資料庫遷移腳本範例

```python
# alembic/versions/xxxx_add_sales_lead_tables.py
"""Add sales lead management tables

Revision ID: xxxx
Revises: 949902ff763d
Create Date: 2026-03-26
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 1. 修改 customers 表
    op.add_column('customers', sa.Column('ad_source', sa.String(100), nullable=True))
    op.add_column('customers', sa.Column('import_batch_id', sa.String(36), nullable=True))
    op.create_foreign_key('fk_customer_import_batch', 'customers', 'import_batches', ['import_batch_id'], ['id'], ondelete='SET NULL')
    op.create_index('idx_ad_source', 'customers', ['ad_source'])
    op.create_index('idx_import_batch_id', 'customers', ['import_batch_id'])

    # 2. 創建 import_batches 表
    op.create_table(
        'import_batches',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('file_name', sa.String(255), nullable=False),
        # ... 其他欄位
    )

    # 3-6. 創建其他表...
    # interactions, ai_analyses, customer_evaluations, health_check_reports

def downgrade():
    # Rollback 邏輯
    pass
```

---

**文件資訊**:
- 版本: 1.0.0
- 最後更新: 2026-03-26
- 狀態: 設計已生成，待審核
- 下一步: 審核設計 → 執行 `/kiro:spec-tasks sales-lead-management -y` 生成實作任務
