# Technical Steering

## Stack

### Backend
- **Framework**: FastAPI 0.109.0 (Python 3.12+)
- **ORM**: SQLAlchemy 2.0.25 (async-capable)
- **Database**: PostgreSQL (asyncpg 0.29.0 driver)
- **Migration**: Alembic 1.13.1
- **Validation**: Pydantic V2 (2.5.3)
- **Server**: Uvicorn 0.27.0 + Gunicorn 21.2.0
- **AI Integration**: OpenAI API 1.12.0
- **Excel Processing**: openpyxl 3.1.2, xlsxwriter 3.1.9
- **Data Analysis**: pandas 2.1.4, numpy 1.26.3

### Frontend
- **Framework**: Vue 3.4.0 + TypeScript 5.3.0
- **Build Tool**: Vite 5.0
- **UI Library**: Element Plus 2.5.0
- **State Management**: Pinia 2.1.0
- **Router**: Vue Router 4.2.0
- **HTTP Client**: Axios 1.6.0
- **Charts**: ECharts 5.5.0 + vue-echarts 6.6.0
- **Form Validation**: VeeValidate 4.12.0 + Yup 1.3.0
- **Date Handling**: dayjs 1.11.0

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Cache**: Redis 5.0.1 (optional)
- **Logging**: Python logging + loguru 0.7.2
- **Error Tracking**: Sentry SDK 1.39.2 (optional)

## Architectural Decisions

### Backend: FastAPI + SQLAlchemy 2.0 Async
**Why FastAPI**:
- 原生支援 async/await，適合高並發場景
- 自動生成 OpenAPI 文檔（/docs），加速前後端對接
- Pydantic 整合，強型別驗證
- 效能優異，適合 AI API 整合場景

**Why SQLAlchemy 2.0**:
- 完整支援 async ORM（與 FastAPI async 一致）
- Type hints 支援，提升開發體驗
- Mapped 類型註解提供更好的型別推斷

### Frontend: Vue 3 + TypeScript
**Why Vue 3**:
- Composition API 提供更好的程式碼組織與重用
- 效能優化（Proxy-based reactivity）
- 生態系成熟（Element Plus、ECharts 完整支援）

**Why TypeScript**:
- 強型別檢查，減少執行時錯誤
- 與 Pydantic schemas 對應，前後端型別一致
- 更好的 IDE 支援與重構能力

### Database: PostgreSQL
**Why PostgreSQL**:
- 完整支援 JSON 型別（問卷資料、KPI 追蹤）
- 成熟的遷移工具（Alembic）
- 優秀的查詢效能與索引支援
- 雲端部署方案成熟（Supabase、Neon、Railway）

### AI Integration: OpenAI API
**Current Implementation**:
- `analyze_conversation()`: 分析業務對話內容
- `extract_customer_info()`: 擷取客戶關鍵資訊
- `assess_aa_customer()`: 評估客戶等級
- Model: GPT-4o-mini（平衡成本與效能）

**Design Philosophy**:
- 服務層封裝（`OpenAIService`），避免直接呼叫 API
- 錯誤處理與重試機制（tenacity 3.2.3）
- 溫度設定 0.7（可調整創意度）

## Conventions

### Backend Naming & Structure
- **Models**: SQLAlchemy declarative models，使用 `Mapped` 型別註解
- **Schemas**: Pydantic V2 models（`BaseModel`），request/response 分離
- **CRUD**: 獨立 CRUD 層（`crud/{resource}.py`），封裝資料庫操作
- **Services**: 業務邏輯層（`services/{service}_service.py`），處理複雜邏輯
- **API Routes**: RESTful 設計，版本化路由（`/api/v1/{resource}`）

**File Naming**:
- Models: 單數名詞（`customer.py`, `visit.py`）
- API Routes: 複數名詞（`customers.py`, `visits.py`）
- Services: `{domain}_service.py` 格式

**Database Conventions**:
- Table names: 複數形式（`customers`, `visits`, `contracts`）
- Primary keys: UUID `String(36)` 格式
- Timestamps: `created_at`, `updated_at` 使用 `DateTime(timezone=True)`
- Foreign keys: `{table_singular}_id` 格式（如 `customer_id`, `user_id`）
- Enum columns: 使用 SQLAlchemy `Enum` 型別

### Frontend Naming & Structure
- **Components**: PascalCase（`CustomerList.vue`, `VisitForm.vue`）
- **Views**: 按功能模組組織（`views/{Module}/Index.vue`）
- **API Clients**: 按資源組織（`api/{resource}.ts`）
- **Stores**: Pinia stores 按功能域分離（`stores/{resource}.ts`）

**Import Conventions**:
- 使用 `@/` alias 指向 `src/` 目錄
- 優先使用 named exports
- API 型別與後端 schemas 對應

**TypeScript Conventions**:
- Interface 優先於 Type（公開 API）
- 嚴格模式啟用（`strict: true`）
- 明確型別註解，避免 `any`

### API Design Patterns
- **Versioning**: `/api/v1/` 前綴，未來可擴充 v2
- **Response Format**:
  ```json
  {
    "data": { ... },      // 成功時返回資料
    "message": "...",     // 可選的訊息
    "error": "..."        // 錯誤時返回錯誤訊息
  }
  ```
- **Pagination**: 使用 `skip` 和 `limit` 參數（Query parameters）
- **Filtering**: RESTful query parameters（如 `?status=completed&customer_id=xxx`）

### Error Handling
- **Backend**: FastAPI exception handlers，返回標準化錯誤格式
- **Frontend**: Axios interceptors 統一處理錯誤，Element Plus Message 顯示
- **Logging**: 使用 loguru 記錄錯誤與關鍵操作

## Integration Patterns

### OpenAI API Integration
- **Service Layer**: `OpenAIService` 封裝所有 AI 呼叫
- **Configuration**: API key 與 model 透過環境變數管理
- **Error Handling**: 重試機制（tenacity）+ fallback 策略
- **Data Source**: `questionnaire_30.json` 預載業務 30 問

### Database Migrations
- **Tool**: Alembic
- **Pattern**: 自動生成 + 人工審查
- **Location**: `backend/alembic/versions/`
- **Workflow**:
  1. 修改 models → 2. `alembic revision --autogenerate` → 3. 審查遷移腳本 → 4. `alembic upgrade head`

### File Upload (規劃中)
- **MVP**: 本地檔案系統儲存（`/backend/uploads/`）
- **Production**: S3-compatible storage（可切換）
- **Service**: `FileService` 抽象層（支援多儲存後端）

### CORS Configuration
- **Development**: 允許 `localhost:5173`, `localhost:8080` 等
- **Production**: 限制為實際前端域名
- **Credentials**: 允許（`allow_credentials=True`）

## Development Workflow

### Backend Development
1. 啟動 Docker Compose（PostgreSQL + Redis）
2. 執行遷移：`alembic upgrade head`
3. 啟動開發伺服器：`uvicorn app.main:app --reload --port 8001`
4. 訪問 API 文檔：`http://localhost:8001/docs`

### Frontend Development
1. 安裝依賴：`npm install`
2. 啟動開發伺服器：`npm run dev`（Vite）
3. 訪問應用：`http://localhost:5173`

### Environment Variables
- **Backend**: `.env` 檔案管理（Pydantic Settings）
- **Frontend**: Vite 環境變數（`VITE_` 前綴）
- **Never commit**: `.env` 檔案（使用 `.env.example` 作為範本）

### Port Configuration
為避免與其他專案衝突：
- Backend API: `8001`
- Frontend Dev: `5173`
- PostgreSQL: `5434`（外部訪問）
- Adminer: `8080`

### Code Quality
- **Backend**: Python type hints, Pydantic 驗證
- **Frontend**: TypeScript strict mode, ESLint, Prettier
- **Testing**: 待規劃（pytest + Vue Test Utils）

## Security Considerations

### MVP Simplification
- **無認證機制**: 本版本跳過 JWT 認證（加速 MVP）
- **Future**: 需實作 JWT token + refresh token 機制

### Data Protection
- **API Keys**: 透過環境變數管理，絕不提交到 Git
- **Database Credentials**: Docker secrets 或環境變數
- **CORS**: 限制允許的 origins

### Input Validation
- **Backend**: Pydantic schemas 強制驗證
- **Frontend**: VeeValidate + Yup schema 驗證
- **SQL Injection**: SQLAlchemy ORM 自動防護

---
*Focus: FastAPI async, Vue 3 Composition API, PostgreSQL JSON, OpenAI integration*
