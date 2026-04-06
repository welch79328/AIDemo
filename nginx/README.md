# Nginx 反向代理配置說明

## 架構說明

使用 **Nginx Docker 容器**作為反向代理，統一入口（對外 8087 端口）：

```
瀏覽器 → Nginx 容器 (Port 8087)
           ├─ / → Frontend 容器 (內部 5173)
           └─ /api → Backend 容器 (內部 8000)
```

所有服務都在 Docker Compose 中運行，通過 Docker 內部網路通訊。

**優點：**
- ✅ 對外統一使用 8087 端口（保持原有訪問方式）
- ✅ Frontend 使用相對路徑 `/api`，無需配置 IP
- ✅ 解決 CORS 跨域問題
- ✅ Backend 容器不直接對外暴露，提升安全性

## 部署步驟

### 1. 啟動所有服務

```bash
cd ~/AIDemo

# 拉取最新代碼
git pull origin main

# 啟動所有容器（包含 Nginx）
docker compose up -d

# 查看服務狀態
docker compose ps
```

**就這麼簡單！** 不需要在宿主機安裝 Nginx。

### 2. 配置防火牆/安全組

只需開啟以下端口：
- ✅ **Port 8087** - Nginx 入口（必須）
- ✅ **Port 22** - SSH (管理用)

可以關閉（可選，提升安全性）：
- ❌ Port 8001 (Backend，已由 Nginx 代理，無需直接對外)
- ❌ Port 5173 (Frontend，已由 Nginx 代理，無需直接對外)
- ❌ Port 8080 (Adminer，生產環境建議關閉)

### 3. 驗證部署

```bash
# 測試 Frontend
curl http://localhost/

# 測試 Backend API
curl http://localhost/api/v1/leads/import/history

# 測試 API 文檔
curl http://localhost/docs
```

## 訪問應用

- **應用首頁**: `http://<EC2-IP>/`
- **API 文檔**: `http://<EC2-IP>/docs`
- **健康檢查**: `http://<EC2-IP>/health`

## 常見問題

### 1. 502 Bad Gateway

檢查 Backend/Frontend 是否正常運行：
```bash
docker compose ps
curl http://localhost:8001/docs
curl http://localhost:8087
```

### 2. CORS 錯誤

檢查 Backend CORS 設定是否包含您的域名/IP

### 3. 查看 Nginx 日誌

```bash
sudo tail -f /var/log/nginx/sales-app-access.log
sudo tail -f /var/log/nginx/sales-app-error.log
```

## SSL/HTTPS 配置（選用）

使用 Let's Encrypt 免費 SSL 憑證：

```bash
# 安裝 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 取得憑證（替換成您的域名）
sudo certbot --nginx -d your-domain.com

# 自動更新測試
sudo certbot renew --dry-run
```
