import http from './http'

/**
 * 儀表板統計數據介面
 */
export interface DashboardStatistics {
  // 客戶統計
  total_customers: number
  aa_customers: number
  new_customers_this_month: number

  // 簽約統計
  total_contracts: number
  contracts_this_month: number
  conversion_rate: number

  // 拜訪統計
  total_visits: number
  visits_this_month: number
  pending_first_visit: number
  pending_second_visit: number

  // 客戶狀態統計
  customers_by_status: {
    contacted: number
    first_visit_scheduled: number
    first_visit_done: number
    second_visit_scheduled: number
    second_visit_done: number
    negotiating: number
    signed: number
    lost: number
  }

  // 客戶階段統計
  customers_by_stage: {
    individual: number
    preparing_company: number
    new_company: number
    scaling_up: number
  }

  // 趨勢數據（最近6個月）
  monthly_trends: {
    month: string
    new_customers: number
    new_contracts: number
    visits: number
  }[]
}

/**
 * 最近客戶
 */
export interface RecentCustomer {
  id: string
  company_name: string
  contact_person: string
  contact_phone: string
  customer_stage: string
  current_status: string
  is_aa_customer: boolean
  created_at: string
}

/**
 * 待辦事項
 */
export interface TodoItem {
  id: string
  type: 'visit' | 'follow_up' | 'contract'
  customer_id: string
  customer_name: string
  title: string
  description: string
  due_date: string
  priority: 'high' | 'medium' | 'low'
  completed: boolean
}

/**
 * 需要跟進的客戶
 */
export interface FollowUpCustomer {
  id: string
  company_name: string
  contact_person: string
  last_contact_date: string
  days_since_contact: number
  current_status: string
  next_action: string
}

/**
 * Dashboard API
 */
class DashboardAPI {
  /**
   * 獲取儀表板統計數據
   */
  async getStatistics(): Promise<DashboardStatistics> {
    const response = await http.get('/api/v1/dashboard/statistics')
    return response.data
  }

  /**
   * 獲取最近新增的客戶
   */
  async getRecentCustomers(limit: number = 5): Promise<RecentCustomer[]> {
    const response = await http.get('/api/v1/dashboard/recent-customers', {
      params: { limit }
    })
    return response.data
  }

  /**
   * 獲取待辦事項
   */
  async getTodoList(completed: boolean = false): Promise<TodoItem[]> {
    const response = await http.get('/api/v1/dashboard/todos', {
      params: { completed }
    })
    return response.data
  }

  /**
   * 獲取需要跟進的客戶
   */
  async getFollowUpCustomers(days: number = 7): Promise<FollowUpCustomer[]> {
    const response = await http.get('/api/v1/dashboard/follow-ups', {
      params: { days }
    })
    return response.data
  }

  /**
   * 標記待辦事項為完成
   */
  async completeTodo(todoId: string): Promise<void> {
    await http.put(`/api/v1/dashboard/todos/${todoId}/complete`)
  }
}

export const dashboardApi = new DashboardAPI()
