/**
 * 客戶管理 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  customerApi,
  type Customer,
  type CustomerListItem,
  type CustomerCreateRequest,
  type CustomerUpdateRequest,
  type CustomerQueryParams,
  type CustomerStatistics
} from '@/api/customer'
import { ElMessage } from 'element-plus'

export const useCustomerStore = defineStore('customer', () => {
  // 狀態
  const customers = ref<CustomerListItem[]>([])
  const currentCustomer = ref<Customer | null>(null)
  const statistics = ref<CustomerStatistics | null>(null)
  const total = ref(0)
  const page = ref(1)
  const limit = ref(20)
  const loading = ref(false)

  // 計算屬性
  const totalPages = computed(() => Math.ceil(total.value / limit.value))
  const hasCustomers = computed(() => customers.value.length > 0)

  /**
   * 載入客戶列表
   */
  async function fetchCustomers(params?: CustomerQueryParams) {
    loading.value = true
    try {
      const response = await customerApi.getList({
        page: page.value,
        limit: limit.value,
        ...params
      })
      customers.value = response.customers
      total.value = response.total
      page.value = response.page
      limit.value = response.limit
    } catch (error) {
      console.error('載入客戶列表失敗:', error)
      ElMessage.error('載入客戶列表失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 載入客戶詳情
   */
  async function fetchCustomerById(id: string) {
    loading.value = true
    try {
      currentCustomer.value = await customerApi.getById(id)
      return currentCustomer.value
    } catch (error) {
      console.error('載入客戶詳情失敗:', error)
      ElMessage.error('載入客戶詳情失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 建立客戶
   */
  async function createCustomer(data: CustomerCreateRequest) {
    loading.value = true
    try {
      const newCustomer = await customerApi.create(data)
      ElMessage.success('客戶建立成功')
      // 重新載入列表
      await fetchCustomers()
      return newCustomer
    } catch (error) {
      console.error('建立客戶失敗:', error)
      ElMessage.error('建立客戶失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新客戶
   */
  async function updateCustomer(id: string, data: CustomerUpdateRequest) {
    loading.value = true
    try {
      const updatedCustomer = await customerApi.update(id, data)
      ElMessage.success('客戶更新成功')
      // 更新列表中的客戶資料
      const index = customers.value.findIndex(c => c.id === id)
      if (index !== -1) {
        customers.value[index] = { ...customers.value[index], ...updatedCustomer }
      }
      // 如果是當前客戶，也更新
      if (currentCustomer.value?.id === id) {
        currentCustomer.value = updatedCustomer
      }
      return updatedCustomer
    } catch (error) {
      console.error('更新客戶失敗:', error)
      ElMessage.error('更新客戶失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 刪除客戶
   */
  async function deleteCustomer(id: string) {
    loading.value = true
    try {
      await customerApi.delete(id)
      ElMessage.success('客戶刪除成功')
      // 從列表中移除
      customers.value = customers.value.filter(c => c.id !== id)
      total.value -= 1
      // 如果是當前客戶，清空
      if (currentCustomer.value?.id === id) {
        currentCustomer.value = null
      }
    } catch (error) {
      console.error('刪除客戶失敗:', error)
      ElMessage.error('刪除客戶失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 載入統計資料
   */
  async function fetchStatistics() {
    loading.value = true
    try {
      statistics.value = await customerApi.getStatistics()
      return statistics.value
    } catch (error) {
      console.error('載入統計資料失敗:', error)
      ElMessage.error('載入統計資料失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 設定分頁
   */
  function setPage(newPage: number) {
    page.value = newPage
  }

  /**
   * 設定每頁數量
   */
  function setLimit(newLimit: number) {
    limit.value = newLimit
    page.value = 1 // 重置到第一頁
  }

  /**
   * 重置狀態
   */
  function reset() {
    customers.value = []
    currentCustomer.value = null
    statistics.value = null
    total.value = 0
    page.value = 1
    limit.value = 20
    loading.value = false
  }

  return {
    // 狀態
    customers,
    currentCustomer,
    statistics,
    total,
    page,
    limit,
    loading,
    // 計算屬性
    totalPages,
    hasCustomers,
    // 方法
    fetchCustomers,
    fetchCustomerById,
    createCustomer,
    updateCustomer,
    deleteCustomer,
    fetchStatistics,
    setPage,
    setLimit,
    reset
  }
})
