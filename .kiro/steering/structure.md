# Structure Steering

## Organization Pattern

### Backend: Layered Architecture
採用分層架構模式，依職責清晰分離各層：

```
backend/app/
├── api/v1/          # API 路由層（HTTP 介面）
├── services/        # 業務邏輯層（複雜邏輯）
├── crud/            # 資料存取層（CRUD 操作）
├── models/          # 資料模型層（SQLAlchemy ORM）
├── schemas/         # 資料驗證層（Pydantic schemas）
├── core/            # 核心配置（config, database）
├── utils/           # 工具函式
└── data/            # 靜態資料（如 questionnaire_30.json）
```

**職責分離原則**:
- API 層僅處理 HTTP 請求/回應，委派給 service/crud
- Service 層處理業務邏輯、第三方整合（如 OpenAI）
- CRUD 層專注於資料庫操作，返回 ORM models
- Schemas 定義 API 合約（request/response）

### Frontend: Feature-First + Layered
按功能模組組織頁面，技術層面分離狀態管理與 API 通訊：

```
frontend/src/
├── views/{Module}/  # 功能模組頁面（Dashboard, Customers, Visits）
│   ├── Index.vue    # 列表/首頁
│   └── Detail.vue   # 詳情頁
├── components/      # 可重用元件（待擴充）
├── stores/          # Pinia 狀態管理（按資源分離）
├── api/             # API 客戶端（按資源分離）
├── router/          # 路由配置
└── assets/          # 靜態資源
```

**模組獨立性**:
- 每個 view 模組（如 Customers, Visits）相對獨立
- 共用邏輯抽取到 stores 和 api 層
- 組件庫（Element Plus）統一註冊於 main.ts

## Module Boundaries

### Backend Layer Separation

**API Layer** (`api/v1/{resource}.py`):
- 定義路由與 HTTP 方法
- 使用 Pydantic schemas 驗證輸入/輸出
- 呼叫 service 或 crud 層
- 處理 HTTP 狀態碼與錯誤回應

**Service Layer** (`services/{service}_service.py`):
- 處理複雜業務邏輯（如 AI 分析、成熟度計算）
- 整合多個 CRUD 操作
- 第三方 API 整合（OpenAI, 檔案上傳）
- 不直接處理 HTTP 請求

**CRUD Layer** (`crud/{resource}.py`):
- 封裝資料庫 CRUD 操作
- 返回 SQLAlchemy models（非 schemas）
- 處理查詢、過濾、分頁
- 不包含業務邏輯

**Models Layer** (`models/base.py`):
- SQLAlchemy declarative models
- 定義資料表結構、關聯、索引
- Enum 定義集中管理

**Schemas Layer** (`schemas/{resource}.py`):
- Pydantic V2 models
- Request schemas（Create, Update）與 Response schemas 分離
- 與 models 對應但不完全相同（API 合約 vs 資料庫結構）

### Frontend Layer Separation

**Views Layer** (`views/{Module}/`):
- 頁面級元件，對應路由
- 組合多個子元件
- 呼叫 stores 或直接呼叫 API
- 處理頁面級狀態與導航

**Stores Layer** (`stores/{resource}.ts`):
- Pinia stores 管理全域/共享狀態
- 提供 actions 封裝 API 呼叫
- 快取資料、避免重複請求

**API Layer** (`api/{resource}.ts`):
- Axios 客戶端封裝
- 定義 TypeScript 介面（對應後端 schemas）
- 統一錯誤處理（interceptors）

## Import Conventions

### Backend Import Pattern
```python
# 標準庫 → 第三方庫 → 本地模組
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.base import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.crud.customer import customer_crud
```

**規則**:
- 使用絕對導入（從 `app.` 開始）
- 分組：stdlib → third-party → local
- 避免循環導入（API → Service/CRUD → Models/Schemas）

### Frontend Import Pattern
```typescript
// Vue/第三方庫 → 本地模組（使用 @ alias）
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import type { Customer } from '@/api/customer'
import { getCustomers } from '@/api/customer'
import { useCustomerStore } from '@/stores/customer'
```

**規則**:
- 使用 `@/` alias 指向 `src/` 目錄
- Type imports 使用 `import type`
- 優先 named exports（非 default）

### Dependency Flow
**Backend**: API → Service → CRUD → Models ← Schemas
- API 依賴 Service/CRUD + Schemas
- Service 依賴 CRUD + Models + 第三方 API
- CRUD 依賴 Models
- Schemas 可引用 Models（但不是強制）

**Frontend**: Views → Stores → API
- Views 依賴 Stores/API
- Stores 依賴 API
- API 層無依賴（僅 axios + types）

## File Naming

### Backend Naming
- **Models**: `base.py`（集中定義所有 models，避免循環導入）
- **Schemas**: `{resource}.py`（如 `customer.py`, `visit.py`）
- **CRUD**: `{resource}.py`（如 `customer.py`, `visit.py`）
- **API Routes**: `{resources}.py`（複數，如 `customers.py`, `visits.py`）
- **Services**: `{domain}_service.py`（如 `openai_service.py`）

### Frontend Naming
- **Views**: `{Module}/{Page}.vue`（PascalCase，如 `Customers/Index.vue`）
- **Components**: `{ComponentName}.vue`（PascalCase）
- **Stores**: `{resource}.ts`（如 `customer.ts`, `visit.ts`）
- **API Clients**: `{resource}.ts`（如 `customer.ts`, `visit.ts`）
- **Types**: 通常與 API client 同檔案，或獨立 `types.ts`

## Key Directories

### Backend Key Directories

**`app/api/v1/`** - API 路由模組
- 每個資源一個檔案（customers.py, visits.py, contracts.py, ai_analysis.py）
- `__init__.py` 統一註冊所有路由到 `api_router`
- 路由前綴：`/api/v1`

**`app/models/base.py`** - 資料模型集中定義
- 所有 SQLAlchemy models 定義於此（避免循環導入）
- Enum 定義集中管理
- 包含關聯定義（relationships）與索引

**`app/services/`** - 業務邏輯服務
- `openai_service.py`: OpenAI API 整合（對話分析、客戶評估）
- 未來可擴充：`excel_service.py`, `file_service.py`, `report_service.py`

**`app/core/`** - 核心配置
- `config.py`: Pydantic Settings（環境變數管理）
- `database.py`: SQLAlchemy async engine + session factory

**`app/data/`** - 靜態資料
- `questionnaire_30.json`: 業務 30 問預載資料

### Frontend Key Directories

**`src/views/`** - 功能模組頁面
- 按功能域組織：`Dashboard/`, `Customers/`, `Visits/`, `Contracts/`, `AIAnalysis/`, `Reports/`
- 每個模組包含 `Index.vue`（列表）和 `Detail.vue`（詳情）

**`src/stores/`** - Pinia 狀態管理
- 按資源分離：`customer.ts`, `visit.ts`, `contract.ts`, `ai.ts`
- 提供 actions 封裝 API 呼叫與狀態管理

**`src/api/`** - API 客戶端
- `http.ts`: Axios 實例配置（base URL, interceptors）
- 資源客戶端：`customer.ts`, `visit.ts`, `contract.ts`, `ai.ts`
- 定義 TypeScript 介面（對應後端 schemas）

**`src/router/`** - 路由配置
- `index.ts`: Vue Router 配置，路由定義與導航守衛

## Special Patterns

### API Versioning
- 所有 API 路由使用 `/api/v1/` 前綴
- 未來新版本可新增 `/api/v2/` 而不影響 v1

### Database Migrations
- `backend/alembic/versions/`: 遷移腳本
- 命名慣例：`{revision}_{description}.py`（Alembic 自動生成）

### Static Data Loading
- `questionnaire_30.json` 在 API 啟動時載入（`ai_analysis.py`）
- 避免重複讀取檔案，提升效能

### Environment Configuration
- **Backend**: `.env` 檔案 + `core/config.py`（Pydantic Settings）
- **Frontend**: Vite 環境變數（`VITE_` 前綴）
- **Never commit**: `.env` 檔案（使用 `.env.example`）

### Docker Structure
```
├── backend/Dockerfile       # FastAPI 容器
├── frontend/Dockerfile      # Vue + Nginx 容器
└── docker-compose.yml       # 編排：backend + frontend + postgres + redis
```

---
*Focus: Layered architecture (backend), Feature-first (frontend), Clear module boundaries*
