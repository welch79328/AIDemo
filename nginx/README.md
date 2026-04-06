# Nginx 反向代理配置說明

## 架構說明

使用 Nginx 作為反向代理，統一入口：

```
瀏覽器 → Nginx (Port 80)
           ├─ / → Frontend (localhost:8087)
           └─ /api → Backend (localhost:8001)
```

## 部署步驟

### 1. 安裝 Nginx

```bash
sudo apt update
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 2. 部署配置檔案

```bash
# 複製配置檔到 Nginx 目錄
sudo cp nginx/sales-app.conf /etc/nginx/sites-available/sales-app

# 創建符號連結啟用網站
sudo ln -s /etc/nginx/sites-available/sales-app /etc/nginx/sites-enabled/

# 刪除預設配置（避免衝突）
sudo rm -f /etc/nginx/sites-enabled/default

# 測試配置
sudo nginx -t

# 重新載入 Nginx
sudo systemctl reload nginx
```

### 3. 配置防火牆/安全組

只需開啟以下端口：
- ✅ **Port 80** - HTTP (必須)
- ✅ **Port 22** - SSH (管理用)
- ✅ **Port 443** - HTTPS (如果使用 SSL)

可以關閉：
- ❌ Port 8087 (Frontend，已由 Nginx 代理)
- ❌ Port 8001 (Backend，已由 Nginx 代理)
- ❌ Port 8080 (Adminer，安全考量)

### 4. 驗證部署

```bash
# 測試 Frontend
curl http://localhost/

# 測試 Backend API
curl http://localhost/api/v1/customers

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
