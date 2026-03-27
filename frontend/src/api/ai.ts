/**
 * AI 分析 API
 */
import http from './http'

// 匹配的問題
export interface MatchedQuestion {
  question_number: number
  question_text: string
  answer: string
  confidence: number
  evidence: string
}

// 客戶資訊
export interface CustomerInfo {
  company_name?: string | null
  property_count?: number | null
  staff_count?: number | null
  business_type?: string | null
  pain_points: string[]
}

// 對談分析回應
export interface ConversationAnalysisResponse {
  matched_questions: MatchedQuestion[]
  summary: string
  customer_info?: CustomerInfo
}

// AA 客戶評估
export interface AACustomerAssessment {
  is_aa_customer: boolean
  confidence: number
  reasons: string[]
  score: number
}

// 問卷問題
export interface QuestionnaireQuestion {
  number: number
  priority: string
  phase: string
  question: string
  options?: string | null
}

// 問卷回應
export interface QuestionnaireResponse {
  questionnaire: QuestionnaireQuestion[]
  total_questions: number
  first_visit_questions: number
  second_visit_questions: number
}

// 音訊轉文字請求
export interface AudioTranscribeRequest {
  interaction_id: string
  language?: string
}

// 音訊轉文字回應
export interface AudioTranscribeResponse {
  interaction_id: string
  transcript_text: string
  audio_duration?: number
  processing_time: number
  ai_model_version: string
}

/**
 * AI 分析 API
 */
export const aiApi = {
  /**
   * 分析對談內容
   */
  analyzeConversation(conversationText: string): Promise<ConversationAnalysisResponse> {
    return http.post('/api/v1/ai/analyze-conversation', {
      conversation_text: conversationText
    })
  },

  /**
   * 提取客戶資訊
   */
  extractCustomerInfo(conversationText: string): Promise<CustomerInfo> {
    return http.post('/api/v1/ai/extract-customer-info', {
      conversation_text: conversationText
    })
  },

  /**
   * 評估 AA 客戶
   */
  assessAACustomer(questionnaireData: Record<string, any>): Promise<AACustomerAssessment> {
    return http.post('/api/v1/ai/assess-aa-customer', {
      questionnaire_data: questionnaireData
    })
  },

  /**
   * 取得問卷結構
   */
  getQuestionnaire(): Promise<QuestionnaireResponse> {
    return http.get('/api/v1/ai/questionnaire')
  },

  /**
   * 音訊轉文字
   */
  transcribeAudio(data: AudioTranscribeRequest): Promise<AudioTranscribeResponse> {
    return http.post('/api/v1/ai/transcribe', data)
  }
}
