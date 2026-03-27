# Frontend Dockerfile - Vue 3 + Vite (MVP 簡化版)
FROM node:20-alpine

# 設定工作目錄
WORKDIR /app

# 複製 package 文件
COPY package*.json ./

# 安裝依賴
RUN npm install

# 複製應用程式碼
COPY . .

# 暴露端口
EXPOSE 5173

# 啟動開發伺服器
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
