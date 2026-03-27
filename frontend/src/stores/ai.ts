/**
 * AI 分析 Store
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  aiApi,
  type ConversationAnalysisResponse,
  type CustomerInfo,
  type AACustomerAssessment,
  type QuestionnaireResponse
} from '@/api/ai'
import { ElMessage } from 'element-plus'

export const useAIStore = defineStore('ai', () => {
  // 狀態
  const analysisResult = ref<ConversationAnalysisResponse | null>(null)
  const customerInfo = ref<CustomerInfo | null>(null)
  const aaAssessment = ref<AACustomerAssessment | null>(null)
  const questionnaire = ref<QuestionnaireResponse | null>(null)
  const loading = ref(false)

  // ============ 拜訪整合相關狀態 ============
  // 追蹤當前對談文字（用於後續儲存）
  const currentConversationText = ref<string>('')

  // 拜訪模式：true 表示從拜訪頁面進入，需要回填資料
  const visitMode = ref<boolean>(false)

  // 目標客戶 ID（拜訪模式使用）
  const targetCustomerId = ref<string | null>(null)

  /**
   * 分析對談
   */
  async function analyzeConversation(conversationText: string) {
    loading.value = true
    try {
      // 儲存對談文字供後續使用
      currentConversationText.value = conversationText

      analysisResult.value = await aiApi.analyzeConversation(conversationText)

      // 同時評估 AA 客戶
      if (analysisResult.value.customer_info) {
        await assessAACustomer(analysisResult.value.customer_info)
      }

      ElMessage.success('對談分析完成')
      return analysisResult.value
    } catch (error) {
      console.error('對談分析失敗:', error)
      ElMessage.error('對談分析失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 啟動拜訪模式（從拜訪頁面進入時呼叫）
   */
  function enableVisitMode(customerId: string) {
    visitMode.value = true
    targetCustomerId.value = customerId
  }

  /**
   * 取得問卷填寫資料（轉換 AI 分析結果為問卷格式）
   */
  function getQuestionnaireData() {
    if (!analysisResult.value) return null

    const questionnaireData: Record<string, any> = {}

    // 將 matched_questions 轉換為問卷格式
    analysisResult.value.matched_questions.forEach(q => {
      // 使用問題編號作為 key（例如 q01, q02）
      const questionKey = `q${q.question_number.toString().padStart(2, '0')}`
      questionnaireData[questionKey] = q.answer
    })

    return questionnaireData
  }

  /**
   * 提取客戶資訊
   */
  async function extractCustomerInfo(conversationText: string) {
    loading.value = true
    try {
      customerInfo.value = await aiApi.extractCustomerInfo(conversationText)
      return customerInfo.value
    } catch (error) {
      console.error('客戶資訊提取失敗:', error)
      ElMessage.error('客戶資訊提取失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 評估 AA 客戶
   */
  async function assessAACustomer(customerData: Record<string, any>) {
    try {
      aaAssessment.value = await aiApi.assessAACustomer(customerData)
      return aaAssessment.value
    } catch (error) {
      console.error('AA 客戶評估失敗:', error)
      // 不顯示錯誤訊息，因為這是附加功能
      return null
    }
  }

  /**
   * 載入問卷結構
   */
  async function fetchQuestionnaire() {
    loading.value = true
    try {
      questionnaire.value = await aiApi.getQuestionnaire()
      return questionnaire.value
    } catch (error) {
      console.error('載入問卷失敗:', error)
      ElMessage.error('載入問卷失敗')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 重置狀態
   */
  function reset() {
    analysisResult.value = null
    customerInfo.value = null
    aaAssessment.value = null
    questionnaire.value = null
    currentConversationText.value = ''
    visitMode.value = false
    targetCustomerId.value = null
    loading.value = false
  }

  return {
    // 狀態
    analysisResult,
    customerInfo,
    aaAssessment,
    questionnaire,
    loading,
    // 拜訪整合狀態
    currentConversationText,
    visitMode,
    targetCustomerId,
    // 方法
    analyzeConversation,
    extractCustomerInfo,
    assessAACustomer,
    fetchQuestionnaire,
    enableVisitMode,
    getQuestionnaireData,
    reset
  }
})
