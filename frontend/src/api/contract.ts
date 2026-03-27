/**
 * 簽約記錄 API
 */
import http from './http'

// 合約類型枚舉
export enum ContractType {
  PACKAGE_RENTAL = 'package_rental',
  PROPERTY_MGMT = 'property_mgmt',
  SUBLEASE = 'sublease',
  HYBRID = 'hybrid'
}

// 簽約記錄介面
export interface Contract {
  id: string
  customer_id: string
  visit_id?: string
  contract_date: string
  contract_type: ContractType
  property_count?: number
  monthly_value?: string

  // 導入 KPI
  kpi_property_upload_rate?: string
  kpi_contract_creation_rate?: string
  kpi_billing_active: boolean
  kpi_payment_integrated: boolean
  kpi_notification_setup: boolean
  kpi_sop_established: boolean

  // 導入狀態
  onboarding_success: boolean
  onboarding_date?: string

  created_at: string
  updated_at: string
  created_by?: string
}

// 簽約列表項目
export interface ContractListItem {
  id: string
  customer_id: string
  contract_date: string
  contract_type: ContractType
  property_count?: number
  monthly_value?: string
  onboarding_success: boolean
  created_at: string
}

// 簽約列表回應
export interface ContractListResponse {
  contracts: ContractListItem[]
  total: number
  page: number
  limit: number
  total_pages: number
}

// 建立簽約記錄請求
export interface ContractCreateRequest {
  customer_id: string
  visit_id?: string
  contract_date: string
  contract_type: ContractType
  property_count?: number
  monthly_value?: string

  // 導入 KPI
  kpi_property_upload_rate?: string
  kpi_contract_creation_rate?: string
  kpi_billing_active?: boolean
  kpi_payment_integrated?: boolean
  kpi_notification_setup?: boolean
  kpi_sop_established?: boolean

  // 導入狀態
  onboarding_success?: boolean
  onboarding_date?: string
}

// 更新簽約記錄請求
export interface ContractUpdateRequest {
  visit_id?: string
  contract_date?: string
  contract_type?: ContractType
  property_count?: number
  monthly_value?: string

  // 導入 KPI
  kpi_property_upload_rate?: string
  kpi_contract_creation_rate?: string
  kpi_billing_active?: boolean
  kpi_payment_integrated?: boolean
  kpi_notification_setup?: boolean
  kpi_sop_established?: boolean

  // 導入狀態
  onboarding_success?: boolean
  onboarding_date?: string
}

// 簽約統計
export interface ContractStatistics {
  total_contracts: number
  package_rental_contracts: number
  property_mgmt_contracts: number
  sublease_contracts: number
  hybrid_contracts: number
  onboarding_success_count: number
  onboarding_success_rate: number
  avg_property_count: number
  total_monthly_value: string
  by_type: Record<string, number>
  by_month: Record<string, number>
}

// KPI 進度
export interface ContractKPIProgress {
  contract_id: string
  customer_name: string
  contract_date: string
  kpi_property_upload_rate?: string
  kpi_contract_creation_rate?: string
  kpi_billing_active: boolean
  kpi_payment_integrated: boolean
  kpi_notification_setup: boolean
  kpi_sop_established: boolean
  kpi_completion_rate: number
  onboarding_success: boolean
}

// 查詢參數
export interface ContractQueryParams {
  page?: number
  limit?: number
  customer_id?: string
  contract_type?: ContractType
  onboarding_success?: boolean
  date_from?: string
  date_to?: string
}

/**
 * 簽約記錄 API
 */
export const contractApi = {
  /**
   * 取得簽約記錄列表
   */
  getList(params?: ContractQueryParams): Promise<ContractListResponse> {
    return http.get('/api/v1/contracts', { params })
  },

  /**
   * 取得簽約記錄詳情
   */
  getById(id: string): Promise<Contract> {
    return http.get(`/api/v1/contracts/${id}`)
  },

  /**
   * 建立簽約記錄
   */
  create(data: ContractCreateRequest): Promise<Contract> {
    return http.post('/api/v1/contracts', data)
  },

  /**
   * 更新簽約記錄
   */
  update(id: string, data: ContractUpdateRequest): Promise<Contract> {
    return http.patch(`/api/v1/contracts/${id}`, data)
  },

  /**
   * 刪除簽約記錄
   */
  delete(id: string): Promise<void> {
    return http.delete(`/api/v1/contracts/${id}`)
  },

  /**
   * 取得簽約統計
   */
  getStatistics(): Promise<ContractStatistics> {
    return http.get('/api/v1/contracts/statistics')
  },

  /**
   * 取得 KPI 進度列表
   */
  getKPIProgress(): Promise<ContractKPIProgress[]> {
    return http.get('/api/v1/contracts/kpi-progress')
  },

  /**
   * 取得特定客戶的簽約記錄
   */
  getCustomerContracts(customerId: string, contractType?: ContractType): Promise<Contract[]> {
    const params = contractType ? { contract_type: contractType } : {}
    return http.get(`/api/v1/contracts/customer/${customerId}/list`, { params })
  }
}
