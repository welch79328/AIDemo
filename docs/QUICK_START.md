# 快速啟動指南

## 📋 前置需求

### 必要軟體
- **Docker**: 20.10+ & Docker Compose 2.0+
- **Git**: 2.x+

### 可選軟體（本地開發）
- **Python**: 3.12+
- **Node.js**: 20+
- **PostgreSQL**: 16+

---

## 🚀 使用 Docker 快速啟動（推薦）

### 1. 克隆專案
```bash
git clone https://github.com/welch79328/AIDemo.git
cd AIDemo
```

### 2. 設定環境變數
```bash
# 複製環境變數範例檔案
cp .env.example .env

# 編輯 .env 檔案，修改必要的設定（至少要改 SECRET_KEY）
# macOS/Linux
nano .env

# Windows
notepad .env
```

**重要設定：**
```env
# 修改為強密碼
DB_PASSWORD=your_strong_password_here

# 修改為 32 字元以上的隨機字串
SECRET_KEY=your-secret-key-at-least-32-characters-long

# 開發環境設定
ENV=development
DEBUG=true
```

### 3. 啟動所有服務（開發環境）
```bash
# 啟動所有服務（前端 + 後端 + 資料庫 + Redis + Adminer）
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
```

### 4. 初始化資料庫
```bash
# 執行資料庫遷移
docker-compose exec backend alembic upgrade head

# 建立初始管理員帳號（選用）
docker-compose exec backend python scripts/create_admin.py
```

### 5. 訪問應用

| 服務 | URL | 說明 |
|-----|-----|------|
| **前端** | http://localhost:5173 | Vue 3 應用程式 |
| **後端 API** | http://localhost:8001 | FastAPI REST API |
| **API 文檔** | http://localhost:8001/docs | Swagger UI（互動式 API 文檔）|
| **ReDoc** | http://localhost:8001/redoc | 另一種 API 文檔格式 |
| **Adminer** | http://localhost:8080 | 資料庫管理介面 |
| **PostgreSQL** | localhost:5434 | 資料庫外部訪問端口 |

**Adminer 登入資訊：**
- 系統：PostgreSQL
- 伺服器：postgres
- 使用者名稱：postgres
- 密碼：（.env 中設定的 DB_PASSWORD）
- 資料庫：sales_performance

### 6. 停止服務
```bash
# 停止所有服務
docker-compose down

# 停止並刪除所有資料（包含資料庫）
docker-compose down -v
```

---

## 🛠️ 本地開發（不使用 Docker）

### 後端設定

#### 1. 安裝 Python 依賴
```bash
cd backend

# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### 2. 設定本地 PostgreSQL
```bash
# 安裝 PostgreSQL（macOS）
brew install postgresql@16
brew services start postgresql@16

# 建立資料庫
createdb sales_performance

# 更新 .env 中的 DATABASE_URL
# 注意：如果使用 Docker 容器的 PostgreSQL，端口為 5434
DATABASE_URL=postgresql+asyncpg://postgres:@localhost:5434/sales_performance
# 或本地安裝的 PostgreSQL（預設端口 5432）
# DATABASE_URL=postgresql+asyncpg://postgres:@localhost:5432/sales_performance
```

#### 3. 執行資料庫遷移
```bash
# 初始化 Alembic（僅首次）
alembic init alembic

# 執行遷移
alembic upgrade head
```

#### 4. 啟動後端開發伺服器
```bash
# 開發模式（支援熱重載）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端設定

#### 1. 安裝 Node.js 依賴
```bash
cd frontend

# 安裝依賴
npm install
```

#### 2. 啟動前端開發伺服器
```bash
# 開發模式（支援熱重載）
npm run dev
```

訪問 http://localhost:5173

---

## 📊 開發工具

### 1. 資料庫遷移

#### 建立新的遷移
```bash
docker-compose exec backend alembic revision --autogenerate -m "描述變更內容"
```

#### 升級資料庫
```bash
docker-compose exec backend alembic upgrade head
```

#### 降級資料庫
```bash
docker-compose exec backend alembic downgrade -1
```

### 2. 測試

#### 執行後端測試
```bash
# 使用 Docker
docker-compose exec backend pytest

# 本地環境
cd backend
pytest

# 顯示覆蓋率
pytest --cov=app --cov-report=html
```

#### 執行前端測試
```bash
# 使用 Docker
docker-compose exec frontend npm run test

# 本地環境
cd frontend
npm run test
```

### 3. 代碼格式化與檢查

#### 後端
```bash
# 格式化代碼
docker-compose exec backend black .

# 排序 imports
docker-compose exec backend isort .

# 代碼檢查
docker-compose exec backend flake8
docker-compose exec backend mypy app
```

#### 前端
```bash
# 格式化代碼
docker-compose exec frontend npm run format

# 代碼檢查
docker-compose exec frontend npm run lint
```

### 4. 產生測試資料

```bash
# 執行種子腳本（產生範例資料）
docker-compose exec backend python scripts/seed_data.py
```

---

## 🔧 常見問題

### 1. 容器無法啟動

**檢查 Docker 狀態：**
```bash
docker --version
docker-compose --version
docker ps
```

**查看詳細錯誤：**
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

### 2. 資料庫連線失敗

**確認 PostgreSQL 容器運行：**
```bash
docker-compose ps postgres
```

**測試資料庫連線：**
```bash
docker-compose exec postgres psql -U postgres -d sales_performance
```

### 3. 端口被佔用

**修改 docker-compose.yml 中的端口映射：**
```yaml
# 例如將前端端口改為 3000
frontend:
  ports:
    - "3000:5173"
```

### 4. 前端無法連接後端 API

**檢查 CORS 設定：**
確認 `.env` 中的 `CORS_ORIGINS` 包含前端 URL：
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 5. 清除所有資料重新開始

```bash
# 停止並刪除所有容器和資料
docker-compose down -v

# 刪除所有映像（可選）
docker-compose down --rmi all

# 重新啟動
docker-compose up -d
```

---

## 📝 進階配置

### 生產環境部署

#### 1. 使用生產配置啟動
```bash
# 啟動 Nginx 反向代理
docker-compose --profile production up -d
```

#### 2. 設定 SSL/TLS
```bash
# 將 SSL 憑證放置在 nginx/ssl/ 目錄
cp your-cert.pem nginx/ssl/cert.pem
cp your-key.pem nginx/ssl/key.pem

# 更新 .env
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem
```

### 效能優化

#### 1. 啟用 Redis 快取
```bash
# Redis 已包含在 docker-compose.yml 中
# 確認 .env 設定
REDIS_URL=redis://redis:6379/0
```

#### 2. 調整資料庫連線池
```env
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

### 監控與日誌

#### 1. 查看即時日誌
```bash
# 所有服務
docker-compose logs -f

# 特定服務
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### 2. 設定 Sentry 錯誤追蹤
```env
SENTRY_DSN=your-sentry-dsn-here
SENTRY_ENVIRONMENT=production
```

---

## 🎓 學習資源

### 後端（FastAPI）
- [FastAPI 官方文檔](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 文檔](https://docs.sqlalchemy.org/en/20/)
- [Pydantic V2 文檔](https://docs.pydantic.dev/latest/)

### 前端（Vue 3）
- [Vue 3 官方文檔](https://vuejs.org/)
- [Vite 官方文檔](https://vitejs.dev/)
- [Pinia 狀態管理](https://pinia.vuejs.org/)

### 資料庫
- [PostgreSQL 文檔](https://www.postgresql.org/docs/)
- [Alembic 遷移工具](https://alembic.sqlalchemy.org/)

---

## 🆘 獲取幫助

1. 查看 [API_DESIGN.md](./api-design.md) 了解 API 規範
2. 查看 [MVP_PROJECT_PLAN.md](./MVP_PROJECT_PLAN.md) 了解專案架構
3. 查看 [database_models.py](./database_models.py) 了解資料模型
4. 在 GitHub Issues 中提問

---

**文件版本**: v1.0
**最後更新**: 2026-03-20
