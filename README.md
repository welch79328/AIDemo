# 業務行動成效評估系統 - AIDemo

> **📢 MVP 簡化設計**: 本版本**無需登入認證**，專注核心業務功能，加速開發與驗證。
> 詳細說明請參考 [MVP_SIMPLIFICATION.md](./MVP_SIMPLIFICATION.md)

## 專案簡介

這是一個基於「客戶健檢表 30 問」架構設計的業務行動成效評估系統，旨在幫助業務團隊：
- 系統化記錄客戶拜訪資訊
- 量化評估業務行動成效
- 智能分類客戶優先級
- 追蹤導入成功指標

## 文件導覽

### 📋 核心文件
- **README.md** (本檔案) - 專案總覽與快速開始
- **[MVP_SIMPLIFICATION.md](./docs/MVP_SIMPLIFICATION.md)** - ⭐ MVP 簡化設計說明（重要！）
- **[PROJECT_STATUS.md](./docs/PROJECT_STATUS.md)** - 專案狀態與開發計畫
- **[docs/MVP_PROJECT_PLAN.md](./docs/MVP_PROJECT_PLAN.md)** - 完整的 MVP 專案規劃文件
  - 專案目標與價值主張
  - 技術架構設計
  - 資料模型設計
  - UI/UX 設計規劃
  - 開發階段規劃（8 週 Sprint）
  - 成功指標定義
  - 預算與資源規劃

### 📊 參考資料
- **[docs/data/5.00.8.3_導入顧問服務_業務30問_客戶健檢表.xlsx](./docs/data/5.00.8.3_導入顧問服務_業務30問_客戶健檢表.xlsx)** - 客戶健檢表原始資料
  - 工作表「01 客戶健檢表_30問」：完整問卷架構
  - 工作表「導入成功KPIs」：6 大導入成功指標
  - 工作表「0219 分類問題串」：詳細業務分類問題
  - 工作表「0219 分工」：組織分工架構

## 快速開始

### 1. 閱讀專案規劃
```bash
open MVP_PROJECT_PLAN.md
```

### 2. 專案初始化（待開發）
```bash
# 將在 Phase 1 實作
npm create next-app@latest sales-performance-app
cd sales-performance-app
npm install
```

## 關鍵特色

### 🎯 智能客戶分類
- **AA 客戶自動標記**：基於 4 個關鍵條件
- **成熟度評分**：0-100 分量化評估
- **優先級推薦**：協助業務聚焦高價值客戶

### 📊 業務成效儀表板
- **個人指標**：拜訪次數、轉換率、AA 客戶獲取
- **團隊指標**：整體漏斗轉換、平均週期
- **視覺化圖表**：即時數據洞察

### 📱 移動優先設計
- **響應式介面**：手機、平板、桌面完整支援
- **離線功能**：拜訪現場也能記錄（未來規劃）
- **快速輸入**：智能表單與自動完成

### 🔄 導入成功追蹤
基於 6 大 KPI 指標：
1. 物件管理（上傳率 ≥ 50%）
2. 合約管理（建立率 ≥ 50%）
3. 帳務管理（定期發送）
4. 金流整合
5. 自動通知
6. SOP 操作

## 技術堆疊

### 前端
- **框架**：Vue 3 + TypeScript + Vite
- **UI 組件庫**：Element Plus / Ant Design Vue / Naive UI
- **狀態管理**：Pinia
- **表單**：VeeValidate + Yup / Zod
- **圖表**：Apache ECharts / Chart.js
- **HTTP 客戶端**：Axios

### 後端
- **框架**：Python FastAPI
- **ORM**：SQLAlchemy 2.0（支援 async）
- **資料庫遷移**：Alembic
- **資料驗證**：Pydantic V2
- **認證**：JWT（python-jose）
- **資料庫**：PostgreSQL
- **快取**：Redis

### 容器化與部署
- **容器化**：Docker + Docker Compose
- **前端部署**：Vercel / Netlify / Cloudflare Pages
- **後端部署**：Railway / Render / Fly.io
- **資料庫**：Supabase / Neon / Railway PostgreSQL
- **反向代理**：Nginx
- **CI/CD**：GitHub Actions

## 開發時程

| 階段 | 週數 | 主要任務 |
|-----|------|---------|
| Phase 1 | Week 1-2 | 基礎架構與認證系統 |
| Phase 2 | Week 3-5 | 核心功能開發 |
| Phase 3 | Week 6-7 | 分析與報表 |
| Phase 4 | Week 8 | 測試與部署 |

詳細 Sprint 規劃請參考 `MVP_PROJECT_PLAN.md`

## 成功指標

### MVP 驗收標準
- ✅ 完整記錄一訪/二訪 30 問
- ✅ 自動計算成熟度評分
- ✅ 自動標記 AA 客戶
- ✅ 提供業務儀表板
- ✅ 頁面載入 < 3 秒

### 業務成效目標（上線後 3 個月）
- 🎯 80% 業務每週使用 3+ 次
- 🎯 拜訪資料整理時間減少 60%
- 🎯 AA 客戶識別率提升 40%
- 🎯 導入成功率達到 70%

## 專案結構（規劃中）

```
AIDemo/
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── views/              # 頁面組件
│   │   │   ├── Dashboard/      # 儀表板
│   │   │   ├── Customers/      # 客戶管理
│   │   │   ├── Visits/         # 拜訪記錄
│   │   │   └── Reports/        # 報表分析
│   │   ├── components/         # 通用組件
│   │   │   ├── forms/          # 表單組件
│   │   │   ├── charts/         # 圖表組件
│   │   │   └── layouts/        # 版面組件
│   │   ├── stores/             # Pinia 狀態管理
│   │   ├── router/             # Vue Router 配置
│   │   ├── api/                # API 客戶端
│   │   ├── utils/              # 工具函式
│   │   └── assets/             # 靜態資源
│   ├── Dockerfile              # 前端 Docker 配置
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                    # FastAPI 後端
│   ├── app/
│   │   ├── api/                # API 路由
│   │   │   ├── v1/             # API v1
│   │   │   │   ├── auth.py     # 認證路由
│   │   │   │   ├── customers.py # 客戶管理
│   │   │   │   ├── visits.py    # 拜訪記錄
│   │   │   │   ├── contracts.py # 簽約管理
│   │   │   │   └── dashboard.py # 儀表板
│   │   │   └── deps.py         # 依賴注入
│   │   ├── core/               # 核心配置
│   │   │   ├── config.py       # 應用配置
│   │   │   ├── security.py     # 安全相關
│   │   │   └── database.py     # 資料庫連線
│   │   ├── models/             # SQLAlchemy 模型
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # 業務邏輯層
│   │   ├── crud/               # CRUD 操作
│   │   └── main.py             # 應用入口
│   ├── alembic/                # 資料庫遷移
│   │   └── versions/
│   ├── tests/                  # 測試
│   ├── scripts/                # 工具腳本
│   ├── Dockerfile              # 後端 Docker 配置
│   ├── requirements.txt        # 生產依賴
│   └── requirements-dev.txt    # 開發依賴
│
├── nginx/                      # Nginx 配置（生產環境）
│   ├── nginx.conf
│   └── conf.d/
│
├── docs/                       # 文件
│   ├── MVP_PROJECT_PLAN.md     # MVP 完整規劃
│   ├── EXECUTIVE_SUMMARY.md    # 執行摘要
│   ├── api-design.md           # API 設計文件
│   └── QUICK_START.md          # 快速啟動指南
│
├── docker-compose.yml          # Docker Compose 配置
├── .env.example                # 環境變數範例
├── .gitignore
├── README.md
└── database_models.py          # SQLAlchemy 資料模型定義
```

## 快速啟動

### 1. 啟動 Docker 容器
```bash
# 設定環境變數
cp .env.example .env

# 啟動所有服務
docker-compose up -d

# 查看服務狀態
docker-compose ps
```

### 2. 訪問應用
- **前端**: http://localhost:5173
- **後端 API**: http://localhost:8001
- **API 文檔**: http://localhost:8001/docs
- **資料庫管理**: http://localhost:8080
- **PostgreSQL**: localhost:5434（外部訪問）

詳細說明請參考 [docs/QUICK_START.md](./docs/QUICK_START.md)

---

## 下一步行動

### 立即執行
1. [x] 完成 MVP 規劃文件
2. [x] 確認技術架構選型（Python FastAPI + Vue 3）
3. [x] 建立 Docker 容器化配置
4. [ ] 組建開發團隊
5. [ ] UI/UX 設計啟動

### 本週目標
1. [ ] 建立後端專案結構（FastAPI）
2. [ ] 建立前端專案結構（Vue 3）
3. [ ] 實作資料庫 models 與 migrations
4. [ ] Sprint 1 啟動會議

## 聯絡資訊

- **專案負責人**: Product Team
- **技術負責人**: TBD
- **文件版本**: v1.0
- **最後更新**: 2026-03-20

## 授權

待定

---

**注意**: 本專案目前處於規劃階段，實際開發將於 Phase 1 開始。
