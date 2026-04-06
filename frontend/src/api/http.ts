import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

// API 基礎 URL
// 空字串表示使用相對路徑（通過 Nginx 代理）
const baseURL = import.meta.env.VITE_API_BASE_URL !== undefined
  ? import.meta.env.VITE_API_BASE_URL
  : 'http://localhost:8001'

// 建立 axios 實例
const http: AxiosInstance = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 請求攔截器
http.interceptors.request.use(
  (config: any) => {
    // MVP 版本無需認證，直接返回
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 回應攔截器
http.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error) => {
    // 處理錯誤
    if (error.response) {
      switch (error.response.status) {
        case 403:
          console.error('沒有權限')
          break
        case 404:
          console.error('請求的資源不存在')
          break
        case 500:
          console.error('伺服器錯誤')
          break
        default:
          console.error('請求失敗:', error.response.data.message)
      }
    }
    return Promise.reject(error)
  }
)

export default http
