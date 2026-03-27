/**
 * 拜訪記錄 API
 */
import http from './http'

// 拜訪類型枚舉
export enum VisitType {
  FIRST_VISIT = 'first_visit',
  SECOND_VISIT = 'second_visit'
}

// 拜訪狀態枚舉
export enum VisitStatus {
  SCHEDULED = 'scheduled',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

// 拜訪記錄介面
export interface Visit {
  id: string
  customer_id: string
  visit_type: VisitType
  visit_date: string
  visit_status: VisitStatus
  questionnaire_data?: Record<string, any>
  notes?: string
  next_action?: string
  next_visit_date?: string
  created_at: string
  updated_at: string
}

// 拜訪列表項目
export interface VisitListItem {
  id: string
  customer_id: string
  visit_type: VisitType
  visit_date: string
  visit_status: VisitStatus
  notes?: string
  next_visit_date?: string
  created_at: string
  updated_at: string
}

// 拜訪列表回應
export interface VisitListResponse {
  visits: VisitListItem[]
  total: number
  page: number
  limit: number
  total_pages: number
}

// 建立拜訪記錄請求
export interface VisitCreateRequest {
  customer_id: string
  visit_type: VisitType
  visit_date: string
  visit_status?: VisitStatus
  questionnaire_data?: Record<string, any>
  notes?: string
  next_action?: string
  next_visit_date?: string
}

// 更新拜訪記錄請求
export interface VisitUpdateRequest {
  visit_type?: VisitType
  visit_date?: string
  visit_status?: VisitStatus
  questionnaire_data?: Record<string, any>
  notes?: string
  next_action?: string
  next_visit_date?: string
}

// 拜訪統計
export interface VisitStatistics {
  total_visits: number
  first_visits: number
  second_visits: number
  completed_visits: number
  scheduled_visits: number
  by_status: Record<string, number>
}

// 查詢參數
export interface VisitQueryParams {
  page?: number
  limit?: number
  customer_id?: string
  visit_type?: VisitType
  visit_status?: VisitStatus
}

/**
 * 拜訪記錄 API
 */
export const visitApi = {
  /**
   * 取得拜訪記錄列表
   */
  getList(params?: VisitQueryParams): Promise<VisitListResponse> {
    return http.get('/api/v1/visits', { params })
  },

  /**
   * 取得拜訪記錄詳情
   */
  getById(id: string): Promise<Visit> {
    return http.get(`/api/v1/visits/${id}`)
  },

  /**
   * 建立拜訪記錄
   */
  create(data: VisitCreateRequest): Promise<Visit> {
    return http.post('/api/v1/visits', data)
  },

  /**
   * 更新拜訪記錄
   */
  update(id: string, data: VisitUpdateRequest): Promise<Visit> {
    return http.patch(`/api/v1/visits/${id}`, data)
  },

  /**
   * 刪除拜訪記錄
   */
  delete(id: string): Promise<void> {
    return http.delete(`/api/v1/visits/${id}`)
  },

  /**
   * 取得拜訪統計
   */
  getStatistics(): Promise<VisitStatistics> {
    return http.get('/api/v1/visits/statistics')
  },

  /**
   * 取得特定客戶的拜訪記錄
   */
  getCustomerVisits(customerId: string, visitType?: VisitType): Promise<Visit[]> {
    const params = visitType ? { visit_type: visitType } : {}
    return http.get(`/api/v1/visits/customer/${customerId}/list`, { params })
  }
}
