<template>
  <div class="visit-detail">
    <!-- 頁面標題與操作 -->
    <el-page-header @back="handleBack" :icon="ArrowLeft">
      <template #content>
        <div class="header-content">
          <h2>拜訪記錄詳情</h2>
          <div class="header-actions">
            <el-button @click="handleEdit" type="primary">編輯記錄</el-button>
            <el-button @click="handleDelete" type="danger">刪除記錄</el-button>
          </div>
        </div>
      </template>
    </el-page-header>

    <el-divider />

    <!-- 載入中 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 拜訪記錄詳情 -->
    <div v-else-if="visit" class="detail-content">
      <!-- 基本資訊卡片 -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">基本資訊</span>
            <div class="header-tags">
              <el-tag :type="visit.visit_type === 'first_visit' ? 'primary' : 'success'" size="large">
                {{ visit.visit_type === 'first_visit' ? '一訪' : '二訪' }}
              </el-tag>
              <el-tag :type="getVisitStatusType(visit.visit_status)" size="large">
                {{ getVisitStatusLabel(visit.visit_status) }}
              </el-tag>
            </div>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="客戶">
            <el-link type="primary" @click="handleViewCustomer">
              {{ customerName }}
            </el-link>
          </el-descriptions-item>
          <el-descriptions-item label="拜訪類型">
            <el-tag :type="visit.visit_type === 'first_visit' ? 'primary' : 'success'">
              {{ visit.visit_type === 'first_visit' ? '一訪' : '二訪' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="拜訪日期">
            {{ formatDateTime(visit.visit_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="拜訪狀態">
            <el-tag :type="getVisitStatusType(visit.visit_status)">
              {{ getVisitStatusLabel(visit.visit_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="下次拜訪日期" v-if="visit.next_visit_date">
            {{ formatDateTime(visit.next_visit_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="建立時間">
            {{ formatDateTime(visit.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新時間">
            {{ formatDateTime(visit.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 拜訪備註 -->
      <el-card v-if="visit.notes" class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">拜訪備註</span>
          </div>
        </template>
        <div class="notes-content">
          {{ visit.notes }}
        </div>
      </el-card>

      <!-- 下一步行動 -->
      <el-card v-if="visit.next_action" class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">下一步行動</span>
          </div>
        </template>
        <div class="action-content">
          {{ visit.next_action }}
        </div>
      </el-card>

      <!-- 問卷資料 -->
      <el-card v-if="visit.questionnaire_data" class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">問卷資料</span>
            <el-tag>{{ visit.visit_type === 'first_visit' ? '一訪問卷' : '二訪問卷' }}</el-tag>
          </div>
        </template>

        <div class="questionnaire-content">
          <!-- 一訪問卷 -->
          <div v-if="visit.visit_type === 'first_visit'" class="questionnaire-section">
            <el-descriptions :column="1" border>
              <el-descriptions-item
                v-for="(value, key) in visit.questionnaire_data"
                :key="key"
                :label="getQuestionLabel(key)"
              >
                {{ formatQuestionValue(key, value) }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 二訪問卷 -->
          <div v-else class="questionnaire-section">
            <el-descriptions :column="1" border>
              <el-descriptions-item
                v-for="(value, key) in visit.questionnaire_data"
                :key="key"
                :label="getQuestionLabel(key)"
              >
                {{ formatQuestionValue(key, value) }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 原始 JSON 資料 (可折疊) -->
          <el-collapse class="json-collapse">
            <el-collapse-item title="查看原始 JSON 資料" name="json">
              <div class="json-content">
                <pre>{{ JSON.stringify(visit.questionnaire_data, null, 2) }}</pre>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-card>

      <!-- 無問卷資料 -->
      <el-card v-else class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">問卷資料</span>
          </div>
        </template>
        <el-empty description="尚未填寫問卷資料">
          <el-button type="primary" @click="handleEdit">立即填寫</el-button>
        </el-empty>
      </el-card>
    </div>

    <!-- 錯誤訊息 -->
    <el-result v-else icon="error" title="載入失敗" sub-title="無法載入拜訪記錄詳情">
      <template #extra>
        <el-button type="primary" @click="handleBack">返回列表</el-button>
      </template>
    </el-result>

    <!-- 編輯對話框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="編輯拜訪記錄"
      width="800px"
      @close="handleEditDialogClose"
    >
      <el-form
        ref="editFormRef"
        :model="editFormData"
        :rules="editFormRules"
        label-width="120px"
      >
        <el-form-item label="拜訪類型" prop="visit_type">
          <el-radio-group v-model="editFormData.visit_type">
            <el-radio label="first_visit">一訪</el-radio>
            <el-radio label="second_visit">二訪</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="拜訪日期" prop="visit_date">
          <el-date-picker
            v-model="editFormData.visit_date"
            type="datetime"
            placeholder="選擇拜訪日期"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="拜訪狀態" prop="visit_status">
          <el-select v-model="editFormData.visit_status" placeholder="請選擇拜訪狀態">
            <el-option label="已排程" value="scheduled" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>

        <el-divider content-position="left">問卷資料</el-divider>

        <!-- 一訪問卷 -->
        <div v-if="editFormData.visit_type === 'first_visit'">
          <el-form-item label="問題 A1">
            <el-input v-model="questionnaireForm.A1" placeholder="是否有外國房客" />
          </el-form-item>
          <el-form-item label="問題 A2">
            <el-input v-model="questionnaireForm.A2" placeholder="房客比例" />
          </el-form-item>
        </div>

        <!-- 二訪問卷 -->
        <div v-if="editFormData.visit_type === 'second_visit'">
          <el-form-item label="問題 B1">
            <el-input v-model="questionnaireForm.B1" placeholder="公司背景" />
          </el-form-item>
        </div>

        <el-divider />

        <el-form-item label="備註">
          <el-input
            v-model="editFormData.notes"
            type="textarea"
            :rows="3"
            placeholder="請輸入拜訪備註"
          />
        </el-form-item>

        <el-form-item label="下一步行動">
          <el-input
            v-model="editFormData.next_action"
            type="textarea"
            :rows="2"
            placeholder="請輸入下一步行動計劃"
          />
        </el-form-item>

        <el-form-item label="下次拜訪日期">
          <el-date-picker
            v-model="editFormData.next_visit_date"
            type="datetime"
            placeholder="選擇下次拜訪日期"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useVisitStore } from '@/stores/visit'
import { useCustomerStore } from '@/stores/customer'
import type { Visit, VisitUpdateRequest } from '@/api/visit'

const route = useRoute()
const router = useRouter()
const visitStore = useVisitStore()
const customerStore = useCustomerStore()

// 狀態
const loading = ref(false)
const visit = ref<Visit | null>(null)
const editDialogVisible = ref(false)
const submitting = ref(false)

// 問卷表單
const questionnaireForm = ref<Record<string, any>>({
  A1: '',
  A2: '',
  B1: ''
})

// 表單
const editFormRef = ref<FormInstance>()
const editFormData = ref<VisitUpdateRequest & { visit_date?: string }>({
  visit_type: 'first_visit',
  visit_date: '',
  visit_status: 'scheduled',
  notes: '',
  next_action: '',
  next_visit_date: ''
})

const editFormRules: FormRules = {
  visit_type: [
    { required: true, message: '請選擇拜訪類型', trigger: 'change' }
  ],
  visit_date: [
    { required: true, message: '請選擇拜訪日期', trigger: 'change' }
  ],
  visit_status: [
    { required: true, message: '請選擇拜訪狀態', trigger: 'change' }
  ]
}

// 客戶名稱
const customerName = computed(() => {
  if (!visit.value) return ''
  const customer = customerStore.customers.find(c => c.id === visit.value?.customer_id)
  return customer?.company_name || '載入中...'
})

// 載入資料
async function loadData() {
  loading.value = true
  try {
    const visitId = route.params.id as string

    // 載入拜訪記錄詳情
    visit.value = await visitStore.fetchVisitById(visitId)

    // 載入客戶列表 (用於顯示客戶名稱)
    if (customerStore.customers.length === 0) {
      await customerStore.fetchCustomers()
    }
  } catch (error) {
    console.error('載入拜訪記錄詳情失敗:', error)
    ElMessage.error('載入拜訪記錄詳情失敗')
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

// 值代碼對應表
const valueMaps: Record<string, Record<string, string>> = {
  q4_business_stage: {
    a: '個人戶',
    b: '準備成立公司',
    c: '剛成立公司',
    d: '物件量增加想數位升級',
  },
  q5_background: {
    a: '仲介',
    b: '建設',
    c: '家族/集團',
    d: '室內裝修/工程',
    e: '純包租代管/創業',
    f: '旅館短租起家',
    g: '斜槓兼職',
  },
  q7_property_types: {
    a: '共生宅',
    b: '套雅房',
    c: '整層',
    d: '透套',
    e: '共享辦公室&商務中心',
  },
  q14_accounting_method: {
    紙本: '紙本',
    系統: '系統',
    外包: '外包會計人員',
  },
  q20_operation_method: {
    紙本: '紙本',
    系統: '系統',
  },
  q21_website_interest: {
    Y: '有興趣（5000元形象官網）',
    N: '無',
    已有: '已有官網',
  },
}

// 格式化問題值
function formatQuestionValue(key: string, value: any): string {
  // 處理空值
  if (value === null || value === undefined || value === '') {
    return '-'
  }

  // 處理布林值
  if (typeof value === 'boolean') {
    return value ? '是' : '否'
  }

  // 處理陣列（將代碼轉為可讀文字）
  if (Array.isArray(value)) {
    if (value.length === 0) return '-'
    const map = valueMaps[key]
    if (map) {
      return value.map(v => map[v] || v).join('、')
    }
    return value.join('、')
  }

  // 處理有對應表的代碼值
  if (valueMaps[key] && valueMaps[key][value]) {
    return valueMaps[key][value]
  }

  // 處理 Y/N 值
  if (value === 'Y') return '有'
  if (value === 'N') return '無'

  // 其他直接顯示
  return String(value)
}

// 問題標籤（對齊問卷 24 問）
function getQuestionLabel(key: string): string {
  const labels: Record<string, string> = {
    // 基本資訊 (1-10)
    q1_website: 'Q1. 公司官網/FB',
    q1_link: 'Q1. 官網/FB 連結',
    q2_line_type: 'Q2. LINE 管理租客',
    q3_company_name: 'Q3. 公司/品牌名稱',
    q4_business_stage: 'Q4. 經營階段',
    q5_background: 'Q5. 公司背景',
    q6_property_ratio: 'Q6. 物件比例（包租/代管）',
    q7_property_types: 'Q7. 案場類型',
    q8_locations: 'Q8. 公司分布地點',
    q9_social_housing: 'Q9. 是否經營社宅',
    q10_pain_points: 'Q10. 目前痛點',
    // 進階資訊 (11-24)
    q11_expansion: 'Q11. 是否規劃擴大營運',
    q12_goals: 'Q12. 公司/決策者目標',
    q13_total_properties: 'Q13. 總戶數',
    q13_total_staff: 'Q13. 總人數',
    q13_staff_division: 'Q13. 人員分工',
    q14_accounting_method: 'Q14. 帳務方式',
    q14_payment_details: 'Q14. 收帳/金流細節',
    q15_landlord_count: 'Q15. 大房東數量',
    q15_monthly_report: 'Q15. 需做損益表',
    q16_invoice_needed: 'Q16. 差額發票（包租）',
    q17_tenant_types: 'Q17. 租客取向',
    q18_foreign_tenants: 'Q18. 外籍租客',
    q19_has_accounting: 'Q19. 是否有會計部門',
    q19_accounting_staff: 'Q19. 會計人數',
    q20_operation_method: 'Q20. 作業方式',
    q20_other_systems: 'Q20. 其他協力系統',
    q21_website_interest: 'Q21. 官網需求',
    q22_competitors: 'Q22. 競品',
    q22_other_competitor: 'Q22. 其他競品說明',
    q23_line_group: 'Q23. LINE 拉群/唐三藏',
    q24_decision_makers: 'Q24. 公司決策人員',
  }
  return labels[key] || `問題 ${key}`
}

// 返回列表
function handleBack() {
  router.push('/visits')
}

// 查看客戶
function handleViewCustomer() {
  if (!visit.value) return
  router.push(`/customers/${visit.value.customer_id}`)
}

// 編輯拜訪記錄
function handleEdit() {
  if (!visit.value) return

  // 填充表單資料
  editFormData.value = {
    visit_type: visit.value.visit_type,
    visit_date: visit.value.visit_date,
    visit_status: visit.value.visit_status,
    notes: visit.value.notes,
    next_action: visit.value.next_action,
    next_visit_date: visit.value.next_visit_date
  }

  // 填充問卷資料
  if (visit.value.questionnaire_data) {
    questionnaireForm.value = { ...visit.value.questionnaire_data }
  } else {
    questionnaireForm.value = {
      A1: '',
      A2: '',
      B1: ''
    }
  }

  editDialogVisible.value = true
}

// 提交編輯
async function handleEditSubmit() {
  if (!visit.value) return

  await editFormRef.value?.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        // 組合問卷資料
        const questionnaire: Record<string, any> = {}
        if (editFormData.value.visit_type === 'first_visit') {
          if (questionnaireForm.value.A1) questionnaire.A1 = questionnaireForm.value.A1
          if (questionnaireForm.value.A2) questionnaire.A2 = questionnaireForm.value.A2
        } else {
          if (questionnaireForm.value.B1) questionnaire.B1 = questionnaireForm.value.B1
        }

        const submitData: VisitUpdateRequest = {
          visit_type: editFormData.value.visit_type,
          visit_date: editFormData.value.visit_date,
          visit_status: editFormData.value.visit_status,
          questionnaire_data: Object.keys(questionnaire).length > 0 ? questionnaire : undefined,
          notes: editFormData.value.notes,
          next_action: editFormData.value.next_action,
          next_visit_date: editFormData.value.next_visit_date
        }

        await visitStore.updateVisit(visit.value!.id, submitData)
        editDialogVisible.value = false
        // 重新載入資料
        await loadData()
      } catch (error) {
        console.error('更新拜訪記錄失敗:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

// 關閉編輯對話框
function handleEditDialogClose() {
  editFormRef.value?.resetFields()
  questionnaireForm.value = {
    A1: '',
    A2: '',
    B1: ''
  }
}

// 刪除拜訪記錄
async function handleDelete() {
  if (!visit.value) return

  try {
    await ElMessageBox.confirm(
      '確定要刪除這筆拜訪記錄嗎?此操作無法復原。',
      '刪除確認',
      {
        confirmButtonText: '確定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await visitStore.deleteVisit(visit.value.id)
    ElMessage.success('拜訪記錄已刪除')
    router.push('/visits')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('刪除拜訪記錄失敗:', error)
    }
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.visit-detail {
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

      .header-tags {
        display: flex;
        gap: 10px;
      }
    }
  }

  .notes-content,
  .action-content {
    padding: 15px;
    background-color: #f5f7fa;
    border-radius: 4px;
    line-height: 1.8;
    white-space: pre-wrap;
  }

  .questionnaire-content {
    .questionnaire-section {
      margin-bottom: 20px;
    }

    .json-collapse {
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
}
</style>
