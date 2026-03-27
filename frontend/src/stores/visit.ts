/**
 * 拜訪記錄 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  visitApi,
  type Visit,
  type VisitListItem,
  type VisitCreateRequest,
  type VisitUpdateRequest,
  type VisitQueryParams,
  type VisitStatistics
} from '@/api/visit'
import { ElMessage } from 'element-plus'

export const useVisitStore = defineStore('visit', () => {
  // 狀態
  const visits = ref<VisitListItem[]>([])
  const currentVisit = ref<Visit | null>(null)
  const statistics = ref<VisitStatistics | null>(null)
  const total = ref(0)
  const page = ref(1)
  const limit = ref(20)
  const loading = ref(false)

  // 計算屬性
  const totalPages = computed(() => Math.ceil(total.value / limit.value))
  const hasVisits = computed(() => visits.value.length > 0)

  /**
   * 載入拜訪記錄列表
   */
  async function fetchVisits(params?: VisitQueryParams) {
    loading.value = true
    try {
      const response = await visitApi.getList({
        page: page.value,
        limit: limit.value,
        ...params
      })
      visits.value = response.visits
      total.value = response.total
      page.value = response.page
      limit.value = response.limit
    } catch (error) {
      console.error('載入拜訪記錄列表失敗:', error)
      ElMessage.error('載入拜訪記錄列表失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 載入拜訪記錄詳情
   */
  async function fetchVisitById(id: string) {
    loading.value = true
    try {
      currentVisit.value = await visitApi.getById(id)
      return currentVisit.value
    } catch (error) {
      console.error('載入拜訪記錄詳情失敗:', error)
      ElMessage.error('載入拜訪記錄詳情失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 建立拜訪記錄
   */
  async function createVisit(data: VisitCreateRequest) {
    loading.value = true
    try {
      const newVisit = await visitApi.create(data)
      ElMessage.success('拜訪記錄建立成功')
      // 重新載入列表
      await fetchVisits()
      return newVisit
    } catch (error: any) {
      console.error('建立拜訪記錄失敗:', error)
      // 顯示詳細的驗證錯誤
      if (error?.response?.data?.detail) {
        const details = error.response.data.detail
        if (Array.isArray(details)) {
          const errorMsg = details.map((d: any) => {
            const field = d.loc.join(' > ')
            return `${field}: ${d.msg}`
          }).join('\n')
          ElMessage.error({
            message: `建立拜訪記錄失敗：\n${errorMsg}`,
            duration: 5000
          })
        } else {
          ElMessage.error(`建立拜訪記錄失敗：${details}`)
        }
      } else {
        ElMessage.error('建立拜訪記錄失敗')
      }
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新拜訪記錄
   */
  async function updateVisit(id: string, data: VisitUpdateRequest) {
    loading.value = true
    try {
      const updatedVisit = await visitApi.update(id, data)
      ElMessage.success('拜訪記錄更新成功')
      // 更新列表中的記錄
      const index = visits.value.findIndex(v => v.id === id)
      if (index !== -1) {
        visits.value[index] = { ...visits.value[index], ...updatedVisit }
      }
      // 如果是當前記錄,也更新
      if (currentVisit.value?.id === id) {
        currentVisit.value = updatedVisit
      }
      return updatedVisit
    } catch (error) {
      console.error('更新拜訪記錄失敗:', error)
      ElMessage.error('更新拜訪記錄失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 刪除拜訪記錄
   */
  async function deleteVisit(id: string) {
    loading.value = true
    try {
      await visitApi.delete(id)
      ElMessage.success('拜訪記錄刪除成功')
      // 從列表中移除
      visits.value = visits.value.filter(v => v.id !== id)
      total.value -= 1
      // 如果是當前記錄,清空
      if (currentVisit.value?.id === id) {
        currentVisit.value = null
      }
    } catch (error) {
      console.error('刪除拜訪記錄失敗:', error)
      ElMessage.error('刪除拜訪記錄失敗')
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
      statistics.value = await visitApi.getStatistics()
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
   * 載入客戶的拜訪記錄
   */
  async function fetchCustomerVisits(customerId: string, visitType?: any) {
    loading.value = true
    try {
      const customerVisits = await visitApi.getCustomerVisits(customerId, visitType)
      return customerVisits
    } catch (error) {
      console.error('載入客戶拜訪記錄失敗:', error)
      ElMessage.error('載入客戶拜訪記錄失敗')
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
    visits.value = []
    currentVisit.value = null
    statistics.value = null
    total.value = 0
    page.value = 1
    limit.value = 20
    loading.value = false
  }

  return {
    // 狀態
    visits,
    currentVisit,
    statistics,
    total,
    page,
    limit,
    loading,
    // 計算屬性
    totalPages,
    hasVisits,
    // 方法
    fetchVisits,
    fetchVisitById,
    createVisit,
    updateVisit,
    deleteVisit,
    fetchStatistics,
    fetchCustomerVisits,
    setPage,
    setLimit,
    reset
  }
})
