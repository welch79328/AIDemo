/**
 * 潛在客戶導入 API
 */
import http from './http'
import axios from 'axios'

// 導入批次狀態枚舉
export enum ImportBatchStatus {
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  PARTIAL_SUCCESS = 'partial_success'
}

// 重複處理策略枚舉
export enum DuplicateStrategy {
  SKIP = 'skip',
  UPDATE = 'update',
  KEEP_BOTH = 'keep_both'
}

// 導入選項
export interface ImportOptions {
  duplicate_strategy?: DuplicateStrategy
  skip_validation?: boolean
}

// 導入結果
export interface LeadImportResponse {
  batch_id: string
  total_rows: number
  successful_imports: number
  failed_imports: number
  duplicate_count: number
  duplicates?: Array<{
    row_number: number
    reason: string
    data: Record<string, any>
  }>
  errors?: Array<{
    row: number
    field: string
    message: string
  }>
  created_at: string
}

// 導入批次摘要
export interface ImportBatchSummary {
  id: string
  file_name: string
  status: ImportBatchStatus
  total_rows: number
  successful_imports: number
  failed_imports: number
  duplicate_count: number
  error_log?: Record<string, any>
  created_at: string
  completed_at?: string
}

// 導入歷史列表回應
export interface ImportHistoryResponse {
  batches: ImportBatchSummary[]
  total: number
  page: number
  limit: number
  total_pages: number
}

// 查詢參數
export interface ImportHistoryQueryParams {
  page?: number
  limit?: number
  status?: ImportBatchStatus
}

// 上傳進度回調
export interface UploadProgressCallback {
  (progressEvent: { loaded: number; total?: number; percentage?: number }): void
}

/**
 * 潛在客戶導入 API
 */
export const leadApi = {
  /**
   * 導入 Excel 名單
   */
  importLeads(
    file: File,
    options?: ImportOptions,
    onUploadProgress?: UploadProgressCallback
  ): Promise<LeadImportResponse> {
    const formData = new FormData()
    formData.append('file', file)

    if (options?.duplicate_strategy) {
      formData.append('duplicate_strategy', options.duplicate_strategy)
    }
    if (options?.skip_validation !== undefined) {
      formData.append('skip_validation', String(options.skip_validation))
    }

    // 使用 axios 直接請求，不通過 http 攔截器（因為需要特殊的 Content-Type）
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

    return axios.post(`${baseURL}/api/v1/leads/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, // 2 分鐘超時（Excel 處理可能較慢）
      onUploadProgress: (progressEvent) => {
        if (onUploadProgress && progressEvent.total) {
          const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onUploadProgress({
            loaded: progressEvent.loaded,
            total: progressEvent.total,
            percentage,
          })
        }
      },
    }).then(res => res.data)
  },

  /**
   * 取得導入歷史記錄
   */
  getImportHistory(params?: ImportHistoryQueryParams): Promise<ImportHistoryResponse> {
    return http.get('/api/v1/leads/import/history', { params })
  },

  /**
   * 取得單一導入批次詳情
   */
  getImportBatch(batchId: string): Promise<ImportBatchSummary> {
    return http.get(`/api/v1/leads/import/${batchId}`)
  },

  /**
   * 下載導入錯誤報告
   */
  downloadErrorReport(batchId: string): Promise<Blob> {
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

    return axios.get(`${baseURL}/api/v1/leads/import/${batchId}/errors`, {
      responseType: 'blob',
    }).then(res => res.data)
  },

  /**
   * 刪除導入批次
   */
  deleteImportBatch(batchId: string): Promise<void> {
    return http.delete(`/api/v1/leads/import/${batchId}`)
  }
}
