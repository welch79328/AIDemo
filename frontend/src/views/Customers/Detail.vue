<template>
  <div class="customer-detail">
    <!-- 頁面標題與操作 -->
    <el-page-header @back="handleBack" :icon="ArrowLeft">
      <template #content>
        <div class="header-content">
          <h2>{{ customer?.company_name || '客戶詳情' }}</h2>
          <div class="header-actions">
            <el-button @click="handleEdit" type="primary">編輯客戶</el-button>
            <el-button @click="handleCreateVisit" type="success">新增拜訪記錄</el-button>
          </div>
        </div>
      </template>
    </el-page-header>

    <el-divider />

    <!-- 載入中 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 客戶詳情 -->
    <div v-else-if="customer" class="detail-content">
      <!-- 基本資訊卡片 -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">基本資訊</span>
            <el-tag :type="getStatusType(customer.customer_status)">
              {{ getStatusLabel(customer.customer_status) }}
            </el-tag>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="公司名稱">
            {{ customer.company_name }}
          </el-descriptions-item>
          <el-descriptions-item label="客戶階段">
            <el-tag :type="getStageType(customer.customer_stage)">
              {{ getStageLabel(customer.customer_stage) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="AA 客戶">
            <el-tag :type="customer.is_aa_customer ? 'success' : 'info'">
              {{ customer.is_aa_customer ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="成熟度評分">
            <el-rate
              v-model="customer.maturity_score"
              disabled
              show-score
              text-color="#ff9900"
            />
          </el-descriptions-item>
          <el-descriptions-item label="聯絡人">
            {{ customer.contact_person || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="聯絡電話">
            {{ customer.contact_phone || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="聯絡信箱">
            {{ customer.contact_email || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="地址">
            {{ customer.address || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="建立時間" :span="2">
            {{ formatDateTime(customer.created_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 基本資訊 JSON (如果有) -->
        <div v-if="customer.basic_info" class="json-section">
          <el-divider content-position="left">詳細資訊</el-divider>
          <div class="json-content">
            <pre>{{ JSON.stringify(customer.basic_info, null, 2) }}</pre>
          </div>
        </div>
      </el-card>

      <!-- AA 客戶判定依據 -->
      <el-card v-if="customer.is_aa_customer && customer.aa_criteria" class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">AA 客戶判定依據</span>
          </div>
        </template>
        <div class="json-content">
          <pre>{{ JSON.stringify(customer.aa_criteria, null, 2) }}</pre>
        </div>
      </el-card>

      <!-- 成熟度分析 -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">成熟度分析</span>
          </div>
        </template>
        <div class="maturity-analysis">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="analysis-item">
                <span class="label">當前成熟度:</span>
                <el-rate
                  v-model="customer.maturity_score"
                  disabled
                  show-score
                  text-color="#ff9900"
                />
              </div>
            </el-col>
            <el-col :span="12">
              <div class="analysis-item">
                <span class="label">客戶階段:</span>
                <el-tag :type="getStageType(customer.customer_stage)">
                  {{ getStageLabel(customer.customer_stage) }}
                </el-tag>
              </div>
            </el-col>
          </el-row>
          <el-divider />
          <div v-if="customer.maturity_details" class="json-content">
            <pre>{{ JSON.stringify(customer.maturity_details, null, 2) }}</pre>
          </div>
          <el-empty v-else description="尚無成熟度詳細資料" />
        </div>
      </el-card>

      <!-- 拜訪歷程 -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">拜訪歷程</span>
            <el-button type="primary" size="small" @click="handleCreateVisit">
              新增拜訪記錄
            </el-button>
          </div>
        </template>

        <div v-if="visits.length > 0" class="visit-timeline">
          <el-timeline>
            <el-timeline-item
              v-for="visit in visits"
              :key="visit.id"
              :timestamp="formatDateTime(visit.visit_date)"
              placement="top"
              :type="getVisitTimelineType(visit.visit_status)"
            >
              <el-card>
                <div class="visit-item">
                  <div class="visit-header">
                    <el-tag :type="visit.visit_type === 'first_visit' ? 'primary' : 'success'">
                      {{ visit.visit_type === 'first_visit' ? '一訪' : '二訪' }}
                    </el-tag>
                    <el-tag :type="getVisitStatusType(visit.visit_status)">
                      {{ getVisitStatusLabel(visit.visit_status) }}
                    </el-tag>
                  </div>

                  <div v-if="visit.notes" class="visit-notes">
                    <strong>備註:</strong> {{ visit.notes }}
                  </div>

                  <div v-if="visit.next_action" class="visit-action">
                    <strong>下一步行動:</strong> {{ visit.next_action }}
                  </div>

                  <div v-if="visit.next_visit_date" class="visit-next">
                    <strong>下次拜訪:</strong> {{ formatDateTime(visit.next_visit_date) }}
                  </div>

                  <div class="visit-actions">
                    <el-button type="primary" size="small" text @click="handleViewVisit(visit.id)">
                      查看詳情
                    </el-button>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>

        <el-empty v-else description="尚無拜訪記錄">
          <el-button type="primary" @click="handleCreateVisit">立即新增</el-button>
        </el-empty>
      </el-card>

      <!-- 互動記錄 -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">互動記錄</span>
            <el-button type="primary" size="small" @click="uploadDialogVisible = true">
              上傳檔案
            </el-button>
          </div>
        </template>

        <InteractionTimeline
          ref="timelineRef"
          :customer-id="customer.id"
          @loaded="onInteractionsLoaded"
        />
      </el-card>

      <!-- AI 分析結果 -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">AI 分析結果</span>
            <el-button
              v-if="latestAudioInteraction && !latestAudioInteraction.transcript_text"
              type="primary"
              size="small"
              :loading="transcribing"
              @click="handleTranscribeAudio"
            >
              {{ transcribing ? '轉文字中...' : '音訊轉文字' }}
            </el-button>
          </div>
        </template>

        <AIAnalysisResult
          v-if="latestAIAnalysis"
          :analysis-data="latestAIAnalysis"
          :questionnaire="questionnaireData"
        />
        <el-empty v-else description="尚無 AI 分析資料">
          <template #description>
            <p>請先上傳音訊檔案並進行轉文字，系統將自動進行 AI 分析</p>
          </template>
        </el-empty>
      </el-card>

      <!-- 客戶健檢報告 -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">客戶健檢報告</span>
          </div>
        </template>

        <HealthCheckReport
          ref="reportRef"
          :customer-id="customer.id"
          :evaluation-id="latestEvaluationId"
          @report-generated="handleReportGenerated"
          @report-deleted="handleReportDeleted"
        />
      </el-card>

      <!-- 簽約記錄 (預留) -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">簽約記錄</span>
          </div>
        </template>
        <el-empty description="簽約管理功能開發中" />
      </el-card>
    </div>

    <!-- 錯誤訊息 -->
    <el-result v-else icon="error" title="載入失敗" sub-title="無法載入客戶詳情">
      <template #extra>
        <el-button type="primary" @click="handleBack">返回列表</el-button>
      </template>
    </el-result>

    <!-- 編輯客戶對話框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="編輯客戶"
      width="800px"
      @close="handleEditDialogClose"
    >
      <el-form
        ref="editFormRef"
        :model="editFormData"
        :rules="editFormRules"
        label-width="120px"
      >
        <el-form-item label="公司名稱" prop="company_name">
          <el-input v-model="editFormData.company_name" placeholder="請輸入公司名稱" />
        </el-form-item>

        <el-form-item label="客戶階段" prop="customer_stage">
          <el-select v-model="editFormData.customer_stage" placeholder="請選擇客戶階段">
            <el-option label="潛在客戶" value="potential" />
            <el-option label="接觸中" value="contacted" />
            <el-option label="評估中" value="evaluating" />
            <el-option label="簽約中" value="signing" />
            <el-option label="已成交" value="signed" />
          </el-select>
        </el-form-item>

        <el-form-item label="客戶狀態" prop="customer_status">
          <el-select v-model="editFormData.customer_status" placeholder="請選擇客戶狀態">
            <el-option label="啟用" value="active" />
            <el-option label="停用" value="inactive" />
            <el-option label="潛在客戶" value="potential" />
          </el-select>
        </el-form-item>

        <el-form-item label="成熟度評分">
          <el-rate v-model="editFormData.maturity_score" show-score />
        </el-form-item>

        <el-form-item label="AA 客戶">
          <el-switch v-model="editFormData.is_aa_customer" />
        </el-form-item>

        <el-form-item label="聯絡人">
          <el-input v-model="editFormData.contact_person" placeholder="請輸入聯絡人姓名" />
        </el-form-item>

        <el-form-item label="聯絡電話">
          <el-input v-model="editFormData.contact_phone" placeholder="請輸入聯絡電話" />
        </el-form-item>

        <el-form-item label="聯絡信箱">
          <el-input v-model="editFormData.contact_email" placeholder="請輸入聯絡信箱" />
        </el-form-item>

        <el-form-item label="地址">
          <el-input v-model="editFormData.address" placeholder="請輸入地址" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleEditSubmit" :loading="submitting">
            確定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 檔案上傳對話框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上傳互動記錄檔案"
      width="600px"
      @close="handleUploadDialogClose"
    >
      <el-form :model="uploadFormData" label-width="100px">
        <el-form-item label="檔案類型" required>
          <el-radio-group v-model="uploadFormData.interaction_type">
            <el-radio label="document">文檔</el-radio>
            <el-radio label="audio">音訊</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="標題">
          <el-input
            v-model="uploadFormData.title"
            placeholder="請輸入標題（選填）"
            maxlength="255"
          />
        </el-form-item>

        <el-form-item label="備註">
          <el-input
            v-model="uploadFormData.notes"
            type="textarea"
            :rows="3"
            placeholder="請輸入備註（選填）"
          />
        </el-form-item>

        <el-form-item label="選擇檔案" required>
          <FileUpload
            :accept="uploadAcceptTypes"
            :max-size="uploadMaxSize"
            @upload="handleFileSelected"
          />
        </el-form-item>

        <el-form-item v-if="uploadProgress > 0 && uploadProgress < 100" label="上傳進度">
          <el-progress :percentage="uploadProgress" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="handleUploadSubmit"
            :loading="uploading"
            :disabled="!selectedFile"
          >
            開始上傳
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useCustomerStore } from '@/stores/customer'
import { useVisitStore } from '@/stores/visit'
import type { Customer, CustomerUpdateRequest } from '@/api/customer'
import type { Visit } from '@/api/visit'
import InteractionTimeline from '@/components/common/InteractionTimeline.vue'
import FileUpload from '@/components/common/FileUpload.vue'
import AIAnalysisResult from '@/components/AIAnalysisResult.vue'
import HealthCheckReport from '@/components/HealthCheckReport.vue'
import { uploadInteractionFile, InteractionType, type Interaction, getInteractions } from '@/api/interaction'
import { aiApi, type QuestionnaireQuestion, type AudioTranscribeRequest } from '@/api/ai'

const route = useRoute()
const router = useRouter()
const customerStore = useCustomerStore()
const visitStore = useVisitStore()

// 狀態
const loading = ref(false)
const customer = ref<Customer | null>(null)
const visits = ref<Visit[]>([])
const editDialogVisible = ref(false)
const submitting = ref(false)

// 互動記錄相關狀態
const timelineRef = ref<InstanceType<typeof InteractionTimeline> | null>(null)
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const selectedFile = ref<File | null>(null)
const uploadFormData = ref({
  interaction_type: 'document' as 'document' | 'audio',
  title: '',
  notes: ''
})

// AI 分析相關狀態
const transcribing = ref(false)
const latestAudioInteraction = ref<Interaction | null>(null)
const latestAIAnalysis = ref<any | null>(null)
const questionnaireData = ref<QuestionnaireQuestion[]>([])
const latestEvaluationId = ref<string | undefined>(undefined)

// 報告相關 ref
const reportRef = ref<InstanceType<typeof HealthCheckReport> | null>(null)

// 表單
const editFormRef = ref<FormInstance>()
const editFormData = ref<CustomerUpdateRequest>({
  company_name: '',
  customer_stage: 'potential',
  customer_status: 'active',
  maturity_score: 0,
  is_aa_customer: false,
  contact_person: '',
  contact_phone: '',
  contact_email: '',
  address: ''
})

const editFormRules: FormRules = {
  company_name: [
    { required: true, message: '請輸入公司名稱', trigger: 'blur' }
  ],
  customer_stage: [
    { required: true, message: '請選擇客戶階段', trigger: 'change' }
  ],
  customer_status: [
    { required: true, message: '請選擇客戶狀態', trigger: 'change' }
  ]
}

// 上傳檔案相關計算屬性
const uploadAcceptTypes = computed(() => {
  if (uploadFormData.value.interaction_type === 'document') {
    return '.pdf,.doc,.docx,.jpg,.jpeg,.png'
  } else {
    return '.mp3,.wav,.m4a'
  }
})

const uploadMaxSize = computed(() => {
  // 文檔 10MB, 音訊 50MB
  return uploadFormData.value.interaction_type === 'document' ? 10 * 1024 * 1024 : 50 * 1024 * 1024
})

// 互動記錄處理函數
async function onInteractionsLoaded(interactions: Interaction[]) {
  console.log('Loaded interactions:', interactions.length)

  // 尋找最新的音訊互動記錄
  const audioInteractions = interactions.filter(i => i.interaction_type === 'audio')
  if (audioInteractions.length > 0) {
    latestAudioInteraction.value = audioInteractions[0] // 假設已按時間倒序排列
  }

  // TODO: 載入最新的 AI 分析結果
  // This would require an API endpoint to get AI analysis by customer ID
  // For now, we'll leave it as null until the backend provides this endpoint
}

function handleFileSelected(file: File) {
  selectedFile.value = file
}

async function handleUploadSubmit() {
  if (!selectedFile.value || !customer.value) {
    ElMessage.warning('請先選擇檔案')
    return
  }

  uploading.value = true
  uploadProgress.value = 0

  try {
    await uploadInteractionFile(
      selectedFile.value,
      customer.value.id,
      uploadFormData.value.interaction_type as InteractionType,
      uploadFormData.value.title,
      uploadFormData.value.notes,
      (progress) => {
        uploadProgress.value = progress.percentage || 0
      }
    )

    ElMessage.success('檔案上傳成功')
    uploadDialogVisible.value = false

    // 刷新時間軸
    if (timelineRef.value) {
      timelineRef.value.refresh()
    }
  } catch (error) {
    console.error('檔案上傳失敗:', error)
    ElMessage.error('檔案上傳失敗')
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

function handleUploadDialogClose() {
  // 重置表單
  uploadFormData.value = {
    interaction_type: 'document',
    title: '',
    notes: ''
  }
  selectedFile.value = null
  uploadProgress.value = 0
}

// AI 分析相關函數
async function handleTranscribeAudio() {
  if (!latestAudioInteraction.value) {
    ElMessage.warning('沒有可轉文字的音訊檔案')
    return
  }

  transcribing.value = true

  try {
    const request: AudioTranscribeRequest = {
      interaction_id: latestAudioInteraction.value.id,
      language: 'zh'
    }

    const response = await aiApi.transcribeAudio(request)

    ElMessage.success('音訊轉文字成功，AI 分析進行中...')

    // 更新互動記錄
    if (latestAudioInteraction.value) {
      latestAudioInteraction.value.transcript_text = response.transcript_text
    }

    // 刷新互動時間軸
    if (timelineRef.value) {
      timelineRef.value.refresh()
    }

    // TODO: 載入 AI 分析結果
    // 實際上後端會在轉文字後自動進行 AI 分析
    // 這裡可以輪詢或等待一段時間後載入分析結果
    setTimeout(() => {
      // loadAIAnalysis()
    }, 2000)
  } catch (error: any) {
    console.error('音訊轉文字失敗:', error)
    ElMessage.error(error.message || '音訊轉文字失敗')
  } finally {
    transcribing.value = false
  }
}

async function loadQuestionnaireData() {
  try {
    const response = await aiApi.getQuestionnaire()
    questionnaireData.value = response.questionnaire
  } catch (error) {
    console.error('載入業務30問失敗:', error)
  }
}

// 報告相關處理函數
function handleReportGenerated(reportId: string) {
  console.log('Report generated:', reportId)
  ElMessage.success('健檢報告生成成功')
}

function handleReportDeleted(reportId: string) {
  console.log('Report deleted:', reportId)
}

// 載入資料
async function loadData() {
  loading.value = true
  try {
    const customerId = route.params.id as string

    // 載入客戶詳情
    customer.value = await customerStore.fetchCustomerById(customerId)

    // 載入拜訪記錄
    visits.value = await visitStore.fetchCustomerVisits(customerId)
  } catch (error) {
    console.error('載入客戶詳情失敗:', error)
    ElMessage.error('載入客戶詳情失敗')
  } finally {
    loading.value = false
  }
}

// 格式化日期時間
function formatDateTime(dateString?: string): string {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 狀態標籤類型
function getStatusType(status: string): 'success' | 'warning' | 'info' {
  const types: Record<string, 'success' | 'warning' | 'info'> = {
    active: 'success',
    inactive: 'info',
    potential: 'warning'
  }
  return types[status] || 'info'
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    active: '啟用',
    inactive: '停用',
    potential: '潛在客戶'
  }
  return labels[status] || status
}

// 階段標籤類型
function getStageType(stage: string): 'primary' | 'success' | 'warning' | 'info' | 'danger' {
  const types: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    potential: 'info',
    contacted: 'primary',
    evaluating: 'warning',
    signing: 'success',
    signed: 'success'
  }
  return types[stage] || 'info'
}

function getStageLabel(stage: string): string {
  const labels: Record<string, string> = {
    potential: '潛在客戶',
    contacted: '接觸中',
    evaluating: '評估中',
    signing: '簽約中',
    signed: '已成交'
  }
  return labels[stage] || stage
}

// 拜訪狀態標籤
function getVisitStatusType(status: string): 'primary' | 'success' | 'info' {
  const types: Record<string, 'primary' | 'success' | 'info'> = {
    scheduled: 'primary',
    completed: 'success',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

function getVisitStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    scheduled: '已排程',
    completed: '已完成',
    cancelled: '已取消'
  }
  return labels[status] || status
}

// 時間軸類型
function getVisitTimelineType(status: string): 'primary' | 'success' | 'info' {
  return getVisitStatusType(status)
}

// 返回列表
function handleBack() {
  router.push('/customers')
}

// 編輯客戶
function handleEdit() {
  if (!customer.value) return

  // 填充表單資料
  editFormData.value = {
    company_name: customer.value.company_name,
    customer_stage: customer.value.customer_stage,
    customer_status: customer.value.customer_status,
    maturity_score: customer.value.maturity_score,
    is_aa_customer: customer.value.is_aa_customer,
    contact_person: customer.value.contact_person,
    contact_phone: customer.value.contact_phone,
    contact_email: customer.value.contact_email,
    address: customer.value.address
  }

  editDialogVisible.value = true
}

// 提交編輯
async function handleEditSubmit() {
  if (!customer.value) return

  await editFormRef.value?.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await customerStore.updateCustomer(customer.value!.id, editFormData.value)
        editDialogVisible.value = false
        // 重新載入資料
        await loadData()
      } catch (error) {
        console.error('更新客戶失敗:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

// 關閉編輯對話框
function handleEditDialogClose() {
  editFormRef.value?.resetFields()
}

// 新增拜訪記錄
function handleCreateVisit() {
  if (!customer.value) return
  router.push({
    path: '/visits',
    query: { customer_id: customer.value.id }
  })
}

// 查看拜訪詳情
function handleViewVisit(visitId: string) {
  router.push(`/visits/${visitId}`)
}

onMounted(() => {
  loadData()
  loadQuestionnaireData()
})
</script>

<style scoped lang="scss">
.customer-detail {
  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;

    h2 {
      margin: 0;
      font-size: 20px;
    }

    .header-actions {
      display: flex;
      gap: 10px;
    }
  }

  .loading-container {
    padding: 20px;
  }

  .detail-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .info-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .card-title {
        font-size: 16px;
        font-weight: bold;
      }
    }

    .json-section {
      margin-top: 20px;
    }

    .json-content {
      background-color: #f5f7fa;
      padding: 15px;
      border-radius: 4px;
      overflow-x: auto;

      pre {
        margin: 0;
        font-size: 13px;
        line-height: 1.6;
      }
    }
  }

  .maturity-analysis {
    .analysis-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px;

      .label {
        font-weight: bold;
        min-width: 100px;
      }
    }
  }

  .visit-timeline {
    .visit-item {
      .visit-header {
        display: flex;
        gap: 10px;
        margin-bottom: 10px;
      }

      .visit-notes,
      .visit-action,
      .visit-next {
        margin: 8px 0;
        font-size: 14px;
        color: #606266;
      }

      .visit-actions {
        margin-top: 10px;
        display: flex;
        gap: 10px;
      }
    }
  }
}
</style>
