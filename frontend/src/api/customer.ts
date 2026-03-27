/**
 * 客戶管理 API
 */
import http from './http'

// 客戶狀態枚舉
export enum CustomerStatus {
  CONTACTED = 'contacted',
  FIRST_VISIT_SCHEDULED = 'first_visit_scheduled',
  FIRST_VISIT_DONE = 'first_visit_done',
  SECOND_VISIT_SCHEDULED = 'second_visit_scheduled',
  SECOND_VISIT_DONE = 'second_visit_done',
  NEGOTIATING = 'negotiating',
  SIGNED = 'signed',
  LOST = 'lost'
}

// 客戶經營階段枚舉
export enum CustomerStage {
  INDIVIDUAL = 'individual',
  PREPARING_COMPANY = 'preparing_company',
  NEW_COMPANY = 'new_company',
  SCALING_UP = 'scaling_up'
}

// 客戶介面
export interface Customer {
  id: string
  company_name: string
  contact_person?: string
  contact_phone?: string
  contact_email?: string
  website?: string
  is_aa_customer: boolean
  customer_stage?: CustomerStage
  maturity_score?: number
  current_status: CustomerStatus
  basic_info?: Record<string, any>
  created_at: string
  updated_at: string
}

// 客戶列表項目
export interface CustomerListItem {
  id: string
  company_name: string
  contact_person?: string
  contact_phone?: string
  is_aa_customer: boolean
  customer_stage?: CustomerStage
  maturity_score?: number
  current_status: CustomerStatus
  created_at: string
  updated_at: string
}

// 客戶列表回應
export interface CustomerListResponse {
  customers: CustomerListItem[]
  total: number
  page: number
  limit: number
  total_pages: number
}

// 建立客戶請求
export interface CustomerCreateRequest {
  company_name: string
  contact_person?: string
  contact_phone?: string
  contact_email?: string
  website?: string
  customer_stage?: CustomerStage
  basic_info?: Record<string, any>
}

// 更新客戶請求
export interface CustomerUpdateRequest {
  company_name?: string
  contact_person?: string
  contact_phone?: string
  contact_email?: string
  website?: string
  customer_stage?: CustomerStage
  current_status?: CustomerStatus
  basic_info?: Record<string, any>
  is_aa_customer?: boolean
  maturity_score?: number
}

// 客戶統計
export interface CustomerStatistics {
  total_customers: number
  aa_customers: number
  by_stage: Record<string, number>
  by_status: Record<string, number>
  average_maturity_score?: number
}

// 查詢參數
export interface CustomerQueryParams {
  page?: number
  limit?: number
  search?: string
  is_aa?: boolean
  status?: CustomerStatus
  stage?: CustomerStage
}

/**
 * 客戶 API
 */
export const customerApi = {
  /**
   * 取得客戶列表
   */
  getList(params?: CustomerQueryParams): Promise<CustomerListResponse> {
    return http.get('/api/v1/customers', { params })
  },

  /**
   * 取得客戶詳情
   */
  getById(id: string): Promise<Customer> {
    return http.get(`/api/v1/customers/${id}`)
  },

  /**
   * 建立客戶
   */
  create(data: CustomerCreateRequest): Promise<Customer> {
    return http.post('/api/v1/customers', data)
  },

  /**
   * 更新客戶
   */
  update(id: string, data: CustomerUpdateRequest): Promise<Customer> {
    return http.patch(`/api/v1/customers/${id}`, data)
  },

  /**
   * 刪除客戶
   */
  delete(id: string): Promise<void> {
    return http.delete(`/api/v1/customers/${id}`)
  },

  /**
   * 取得客戶統計
   */
  getStatistics(): Promise<CustomerStatistics> {
    return http.get('/api/v1/customers/statistics')
  }
}
