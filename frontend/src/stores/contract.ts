/**
 * 簽約記錄 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  contractApi,
  type Contract,
  type ContractListItem,
  type ContractCreateRequest,
  type ContractUpdateRequest,
  type ContractQueryParams,
  type ContractStatistics,
  type ContractKPIProgress
} from '@/api/contract'
import { ElMessage } from 'element-plus'

export const useContractStore = defineStore('contract', () => {
  // 狀態
  const contracts = ref<ContractListItem[]>([])
  const currentContract = ref<Contract | null>(null)
  const statistics = ref<ContractStatistics | null>(null)
  const kpiProgress = ref<ContractKPIProgress[]>([])
  const total = ref(0)
  const page = ref(1)
  const limit = ref(20)
  const loading = ref(false)

  // 計算屬性
  const totalPages = computed(() => Math.ceil(total.value / limit.value))
  const hasContracts = computed(() => contracts.value.length > 0)

  /**
   * 載入簽約記錄列表
   */
  async function fetchContracts(params?: ContractQueryParams) {
    loading.value = true
    try {
      const response = await contractApi.getList({
        page: page.value,
        limit: limit.value,
        ...params
      })
      contracts.value = response.contracts
      total.value = response.total
      page.value = response.page
      limit.value = response.limit
    } catch (error) {
      console.error('載入簽約記錄列表失敗:', error)
      ElMessage.error('載入簽約記錄列表失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 載入簽約記錄詳情
   */
  async function fetchContractById(id: string) {
    loading.value = true
    try {
      currentContract.value = await contractApi.getById(id)
      return currentContract.value
    } catch (error) {
      console.error('載入簽約記錄詳情失敗:', error)
      ElMessage.error('載入簽約記錄詳情失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 建立簽約記錄
   */
  async function createContract(data: ContractCreateRequest) {
    loading.value = true
    try {
      const newContract = await contractApi.create(data)
      ElMessage.success('簽約記錄建立成功')
      // 重新載入列表
      await fetchContracts()
      return newContract
    } catch (error) {
      console.error('建立簽約記錄失敗:', error)
      ElMessage.error('建立簽約記錄失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新簽約記錄
   */
  async function updateContract(id: string, data: ContractUpdateRequest) {
    loading.value = true
    try {
      const updatedContract = await contractApi.update(id, data)
      ElMessage.success('簽約記錄更新成功')
      // 更新列表中的記錄
      const index = contracts.value.findIndex(c => c.id === id)
      if (index !== -1) {
        contracts.value[index] = { ...contracts.value[index], ...updatedContract }
      }
      // 如果是當前記錄,也更新
      if (currentContract.value?.id === id) {
        currentContract.value = updatedContract
      }
      return updatedContract
    } catch (error) {
      console.error('更新簽約記錄失敗:', error)
      ElMessage.error('更新簽約記錄失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 刪除簽約記錄
   */
  async function deleteContract(id: string) {
    loading.value = true
    try {
      await contractApi.delete(id)
      ElMessage.success('簽約記錄刪除成功')
      // 從列表中移除
      contracts.value = contracts.value.filter(c => c.id !== id)
      total.value -= 1
      // 如果是當前記錄,清空
      if (currentContract.value?.id === id) {
        currentContract.value = null
      }
    } catch (error) {
      console.error('刪除簽約記錄失敗:', error)
      ElMessage.error('刪除簽約記錄失敗')
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
      statistics.value = await contractApi.getStatistics()
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
   * 載入 KPI 進度
   */
  async function fetchKPIProgress() {
    loading.value = true
    try {
      kpiProgress.value = await contractApi.getKPIProgress()
      return kpiProgress.value
    } catch (error) {
      console.error('載入 KPI 進度失敗:', error)
      ElMessage.error('載入 KPI 進度失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 載入客戶的簽約記錄
   */
  async function fetchCustomerContracts(customerId: string, contractType?: any) {
    loading.value = true
    try {
      const customerContracts = await contractApi.getCustomerContracts(customerId, contractType)
      return customerContracts
    } catch (error) {
      console.error('載入客戶簽約記錄失敗:', error)
      ElMessage.error('載入客戶簽約記錄失敗')
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
    contracts.value = []
    currentContract.value = null
    statistics.value = null
    kpiProgress.value = []
    total.value = 0
    page.value = 1
    limit.value = 20
    loading.value = false
  }

  return {
    // 狀態
    contracts,
    currentContract,
    statistics,
    kpiProgress,
    total,
    page,
    limit,
    loading,
    // 計算屬性
    totalPages,
    hasContracts,
    // 方法
    fetchContracts,
    fetchContractById,
    createContract,
    updateContract,
    deleteContract,
    fetchStatistics,
    fetchKPIProgress,
    fetchCustomerContracts,
    setPage,
    setLimit,
    reset
  }
})
