/**
 * 客戶互動記錄 API
 */
import http from './http'

// 互動類型枚舉
export enum InteractionType {
  DOCUMENT = 'document',
  AUDIO = 'audio',
  STATUS_CHANGE = 'status_change'
}

// 互動記錄介面
export interface Interaction {
  id: string
  customer_id: string
  interaction_type: InteractionType
  title?: string
  notes?: string
  file_path?: string
  file_name?: string
  file_size?: number
  file_type?: string
  audio_duration?: number
  transcript_text?: string
  created_at: string
  updated_at?: string
  created_by?: string
}

// 建立互動記錄請求
export interface InteractionCreate {
  customer_id: string
  interaction_type: InteractionType
  title?: string
  notes?: string
}

// 檔案上傳回應
export interface InteractionUploadResponse {
  id: string
  customer_id: string
  interaction_type: InteractionType
  title?: string
  file_path?: string
  file_name: string
  file_size: number
  audio_duration?: number
  notes?: string
  created_at: string
}

// 列表查詢回應
export interface InteractionListResponse {
  interactions: Interaction[]
  total: number
  page: number
  limit: number
  total_pages: number
}

// 查詢參數
export interface InteractionQueryParams {
  customer_id?: string
  interaction_type?: InteractionType
  page?: number
  limit?: number
}

// 上傳進度回調
export interface UploadProgressCallback {
  (progressEvent: { loaded: number; total?: number; percentage?: number }): void
}

/**
 * 建立互動記錄（非檔案上傳）
 */
export async function createInteraction(data: InteractionCreate): Promise<Interaction> {
  const response = await http.post<Interaction>('/api/v1/interactions', data)
  return response.data
}

/**
 * 上傳檔案並建立互動記錄
 * @param file - 檔案物件
 * @param customerId - 客戶 ID
 * @param interactionType - 互動類型
 * @param title - 標題（可選）
 * @param notes - 備註（可選）
 * @param onProgress - 上傳進度回調（可選）
 */
export async function uploadInteractionFile(
  file: File,
  customerId: string,
  interactionType: InteractionType,
  title?: string,
  notes?: string,
  onProgress?: UploadProgressCallback
): Promise<InteractionUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('customer_id', customerId)
  formData.append('interaction_type', interactionType)
  if (title) {
    formData.append('title', title)
  }
  if (notes) {
    formData.append('notes', notes)
  }

  const response = await http.post<InteractionUploadResponse>(
    '/api/v1/interactions/upload',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress({
            loaded: progressEvent.loaded,
            total: progressEvent.total,
            percentage
          })
        }
      },
      timeout: 120000 // 120 秒超時（檔案上傳可能較慢）
    }
  )

  return response.data
}

/**
 * 查詢互動記錄列表
 * @param params - 查詢參數
 */
export async function getInteractions(
  params?: InteractionQueryParams
): Promise<InteractionListResponse> {
  const response = await http.get<InteractionListResponse>('/api/v1/interactions', {
    params
  })
  return response.data
}

/**
 * 查詢單一互動記錄
 * @param id - 互動記錄 ID
 */
export async function getInteraction(id: string): Promise<Interaction> {
  const response = await http.get<Interaction>(`/api/v1/interactions/${id}`)
  return response.data
}

/**
 * 刪除互動記錄
 * @param id - 互動記錄 ID
 */
export async function deleteInteraction(id: string): Promise<void> {
  await http.delete(`/api/v1/interactions/${id}`)
}
