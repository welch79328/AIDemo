/**
 * 健檢報告 API
 */
import http from './http'

// 客戶分級枚舉
export enum CustomerGrade {
  AA = 'AA',
  A = 'A',
  B = 'B',
  C = 'C'
}

// 報告生成請求
export interface ReportGenerateRequest {
  customer_id: string
  evaluation_id?: string
  format?: 'xlsx' | 'pdf'
  include_ai_analysis?: boolean
}

// 報告生成回應
export interface ReportGenerateResponse {
  report_id: string
  customer_id: string
  file_path: string
  file_format: string
  created_at: string
}

// 報告詳情
export interface ReportResponse {
  id: string
  customer_id: string
  evaluation_id?: string
  report_title: string
  report_content: Record<string, any>
  file_path?: string
  file_format: string
  created_at: string
  created_by?: string
}

// 報告列表項目
export interface ReportListItem {
  id: string
  customer_id: string
  customer_name?: string
  report_title: string
  file_format: string
  created_at: string
}

// 報告列表回應
export interface ReportListResponse {
  reports: ReportListItem[]
  total: number
  page: number
  limit: number
  total_pages: number
}

// 批次匯出請求
export interface BatchExportRequest {
  customer_ids: string[]
  format?: 'xlsx' | 'pdf'
}

// Email 發送請求
export interface ReportEmailRequest {
  report_id: string
  recipient_email: string
  subject?: string
  message?: string
}

// Email 發送回應
export interface ReportEmailResponse {
  success: boolean
  message: string
  sent_at?: string
}

/**
 * 報告 API
 */
export const reportApi = {
  /**
   * 生成健檢報告
   */
  generateReport(data: ReportGenerateRequest): Promise<ReportGenerateResponse> {
    return http.post('/api/v1/reports/generate', data)
  },

  /**
   * 獲取報告列表
   */
  getReports(params?: {
    customer_id?: string
    page?: number
    limit?: number
  }): Promise<ReportListResponse> {
    return http.get('/api/v1/reports', { params })
  },

  /**
   * 獲取單一報告詳情
   */
  getReport(reportId: string): Promise<ReportResponse> {
    return http.get(`/api/v1/reports/${reportId}`)
  },

  /**
   * 匯出報告（下載）
   */
  exportReport(reportId: string): Promise<Blob> {
    return http.get(`/api/v1/reports/${reportId}/export`, {
      responseType: 'blob'
    })
  },

  /**
   * 批次匯出報告（下載 ZIP）
   */
  batchExportReports(data: BatchExportRequest): Promise<Blob> {
    return http.post('/api/v1/reports/batch-export', data, {
      responseType: 'blob'
    })
  },

  /**
   * 透過 Email 發送報告
   */
  sendReportEmail(data: ReportEmailRequest): Promise<ReportEmailResponse> {
    return http.post('/api/v1/reports/send-email', data)
  },

  /**
   * 刪除報告
   */
  deleteReport(reportId: string): Promise<{ message: string }> {
    return http.delete(`/api/v1/reports/${reportId}`)
  },

  /**
   * 下載報告檔案（觸發瀏覽器下載）
   */
  async downloadReport(reportId: string, fileName?: string): Promise<void> {
    const blob = await this.exportReport(reportId)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName || `report_${reportId}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  },

  /**
   * 批次下載報告（觸發瀏覽器下載 ZIP）
   */
  async downloadBatchReports(
    customerIds: string[],
    fileName?: string
  ): Promise<void> {
    const blob = await this.batchExportReports({ customer_ids: customerIds })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName || `reports_batch_${Date.now()}.zip`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }
}
