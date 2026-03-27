<template>
  <div class="health-check-report">
    <!-- 報告列表 -->
    <div class="report-header">
      <h3>客戶健檢報告</h3>
      <el-button
        type="primary"
        :icon="DocumentAdd"
        :loading="generating"
        @click="handleGenerateReport"
      >
        {{ generating ? '生成中...' : '生成新報告' }}
      </el-button>
    </div>

    <!-- 載入狀態 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 錯誤狀態 -->
    <el-alert
      v-else-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      class="error-alert"
    />

    <!-- 報告列表 -->
    <div v-else class="report-content">
      <!-- 報告表格 -->
      <el-table
        v-if="reports.length > 0"
        :data="reports"
        stripe
        style="width: 100%"
        @row-click="handlePreviewReport"
      >
        <el-table-column prop="report_title" label="報告標題" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" :underline="false">
              <el-icon><Document /></el-icon>
              {{ row.report_title }}
            </el-link>
          </template>
        </el-table-column>

        <el-table-column prop="file_format" label="格式" width="80">
          <template #default="{ row }">
            <el-tag :type="row.file_format === 'xlsx' ? 'success' : 'warning'" size="small">
              {{ row.file_format.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="生成時間" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button
                size="small"
                :icon="View"
                @click.stop="handlePreviewReport(row)"
              >
                預覽
              </el-button>
              <el-button
                size="small"
                type="primary"
                :icon="Download"
                @click.stop="handleDownloadReport(row)"
              >
                下載
              </el-button>
              <el-button
                size="small"
                type="info"
                :icon="Message"
                @click.stop="handleShowEmailDialog(row)"
              >
                分享
              </el-button>
              <el-button
                size="small"
                type="danger"
                :icon="Delete"
                @click.stop="handleDeleteReport(row)"
              >
                刪除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 無報告狀態 -->
      <el-empty v-else description="尚無健檢報告">
        <el-button type="primary" @click="handleGenerateReport">
          生成第一份報告
        </el-button>
      </el-empty>

      <!-- 分頁 -->
      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @size-change="loadReports"
        @current-change="loadReports"
      />
    </div>

    <!-- 報告預覽對話框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="報告預覽"
      width="80%"
      :close-on-click-modal="false"
      class="preview-dialog"
    >
      <div v-if="selectedReport" class="report-preview">
        <!-- 報告標題 -->
        <div class="preview-header">
          <h2>{{ selectedReport.report_title }}</h2>
          <el-tag type="info">{{ formatDate(selectedReport.created_at) }}</el-tag>
        </div>

        <!-- 報告內容 -->
        <div v-if="selectedReport.report_content" class="preview-content">
          <!-- 客戶基本資料 -->
          <el-descriptions
            v-if="selectedReport.report_content.customer"
            title="客戶基本資料"
            :column="2"
            border
            class="preview-section"
          >
            <el-descriptions-item label="公司名稱">
              {{ selectedReport.report_content.customer.company_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="聯絡人">
              {{ selectedReport.report_content.customer.contact_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="聯絡電話">
              {{ selectedReport.report_content.customer.contact_phone || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="Email">
              {{ selectedReport.report_content.customer.contact_email || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="地址" :span="2">
              {{ selectedReport.report_content.customer.address || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="廣告來源">
              {{ selectedReport.report_content.customer.ad_source || '-' }}
            </el-descriptions-item>
          </el-descriptions>

          <!-- 評估結果 -->
          <el-descriptions
            v-if="selectedReport.report_content.evaluation"
            title="評估結果"
            :column="2"
            border
            class="preview-section"
          >
            <el-descriptions-item label="客戶等級">
              <el-tag
                :type="getGradeType(selectedReport.report_content.evaluation.grade)"
                size="large"
              >
                {{ selectedReport.report_content.evaluation.grade }} 級
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="評分">
              <el-rate
                :model-value="selectedReport.report_content.evaluation.score / 20"
                disabled
                show-score
                score-template="{value} 分 (總分: {{ selectedReport.report_content.evaluation.score }})"
              />
            </el-descriptions-item>
            <el-descriptions-item
              v-if="selectedReport.report_content.evaluation.coverage_rate"
              label="問題覆蓋率"
            >
              <el-progress
                :percentage="selectedReport.report_content.evaluation.coverage_rate"
                :color="getCoverageColor(selectedReport.report_content.evaluation.coverage_rate)"
              />
            </el-descriptions-item>
            <el-descriptions-item
              v-if="selectedReport.report_content.evaluation.quality_score"
              label="對話品質"
            >
              {{ selectedReport.report_content.evaluation.quality_score }} 分
            </el-descriptions-item>
            <el-descriptions-item
              v-if="selectedReport.report_content.evaluation.aa_reasons"
              label="AA 判定原因"
              :span="2"
            >
              <ul class="aa-reasons-list">
                <li
                  v-for="(reason, idx) in selectedReport.report_content.evaluation.aa_reasons"
                  :key="idx"
                >
                  {{ reason }}
                </li>
              </ul>
            </el-descriptions-item>
          </el-descriptions>

          <!-- 業務30問問答 -->
          <div v-if="selectedReport.report_content.questions" class="preview-section">
            <h3>業務30問問答記錄</h3>
            <el-table :data="selectedReport.report_content.questions" border stripe>
              <el-table-column prop="number" label="編號" width="80" align="center" />
              <el-table-column prop="phase" label="階段" width="100" />
              <el-table-column prop="question" label="問題內容" min-width="200" />
              <el-table-column prop="answer" label="客戶回答" min-width="200">
                <template #default="{ row }">
                  <span v-if="row.answer" class="answer-text">{{ row.answer }}</span>
                  <el-tag v-else type="info" size="small">未討論</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="狀態" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.answer ? 'success' : 'warning'" size="small">
                    {{ row.answer ? '✓ 已討論' : '✗ 未討論' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <el-empty v-else description="無法載入報告內容" />
      </div>

      <template #footer>
        <el-button @click="previewDialogVisible = false">關閉</el-button>
        <el-button type="primary" :icon="Download" @click="handleDownloadReport(selectedReport)">
          下載報告
        </el-button>
        <el-button type="info" :icon="Message" @click="handleShowEmailDialog(selectedReport)">
          Email 分享
        </el-button>
      </template>
    </el-dialog>

    <!-- Email 分享對話框 -->
    <el-dialog
      v-model="emailDialogVisible"
      title="Email 分享報告"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="emailFormRef"
        :model="emailForm"
        :rules="emailRules"
        label-width="100px"
      >
        <el-form-item label="收件人" prop="recipient_email">
          <el-input
            v-model="emailForm.recipient_email"
            placeholder="請輸入收件人 Email"
            type="email"
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="主旨" prop="subject">
          <el-input
            v-model="emailForm.subject"
            placeholder="Email 主旨（可選）"
          />
        </el-form-item>

        <el-form-item label="訊息" prop="message">
          <el-input
            v-model="emailForm.message"
            type="textarea"
            :rows="5"
            placeholder="Email 內容（可選）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="emailDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="sending"
          :icon="Message"
          @click="handleSendEmail"
        >
          {{ sending ? '發送中...' : '發送' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  DocumentAdd,
  Document,
  View,
  Download,
  Message,
  Delete
} from '@element-plus/icons-vue'
import { reportApi, type ReportListItem, type ReportResponse } from '@/api/report'

// Props
interface Props {
  customerId: string
  evaluationId?: string
  autoLoad?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  evaluationId: undefined,
  autoLoad: true
})

// Emits
const emit = defineEmits<{
  reportGenerated: [reportId: string]
  reportDeleted: [reportId: string]
}>()

// Reactive state
const loading = ref(false)
const generating = ref(false)
const sending = ref(false)
const error = ref<string | null>(null)
const reports = ref<ReportListItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// Dialog state
const previewDialogVisible = ref(false)
const emailDialogVisible = ref(false)
const selectedReport = ref<ReportResponse | null>(null)

// Email form
const emailFormRef = ref<FormInstance>()
const emailForm = ref({
  recipient_email: '',
  subject: '',
  message: ''
})

const emailRules: FormRules = {
  recipient_email: [
    { required: true, message: '請輸入收件人 Email', trigger: 'blur' },
    { type: 'email', message: '請輸入有效的 Email 地址', trigger: 'blur' }
  ]
}

// Computed
const hasReports = computed(() => reports.value.length > 0)

// Methods
const formatDate = (dateString: string): string => {
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

const getGradeType = (grade: string): string => {
  const gradeMap: Record<string, string> = {
    'AA': 'success',
    'A': 'primary',
    'B': 'warning',
    'C': 'info'
  }
  return gradeMap[grade] || 'info'
}

const getCoverageColor = (percentage: number): string => {
  if (percentage >= 80) return '#67C23A'
  if (percentage >= 60) return '#E6A23C'
  if (percentage >= 40) return '#F56C6C'
  return '#909399'
}

const loadReports = async () => {
  if (!props.customerId) return

  loading.value = true
  error.value = null

  try {
    const response = await reportApi.getReports({
      customer_id: props.customerId,
      page: currentPage.value,
      limit: pageSize.value
    })

    reports.value = response.reports
    total.value = response.total
  } catch (err: any) {
    error.value = err.message || '載入報告列表失敗'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

const handleGenerateReport = async () => {
  generating.value = true

  try {
    const response = await reportApi.generateReport({
      customer_id: props.customerId,
      evaluation_id: props.evaluationId,
      format: 'xlsx',
      include_ai_analysis: true
    })

    ElMessage.success('報告生成成功')
    emit('reportGenerated', response.report_id)

    // 重新載入報告列表
    await loadReports()
  } catch (err: any) {
    const errorMsg = err.message || '生成報告失敗'
    ElMessage.error(errorMsg)
  } finally {
    generating.value = false
  }
}

const handlePreviewReport = async (report: ReportListItem | ReportResponse) => {
  try {
    // 如果已經有完整資料，直接使用
    if ('report_content' in report) {
      selectedReport.value = report as ReportResponse
    } else {
      // 否則載入完整報告資料
      const fullReport = await reportApi.getReport(report.id)
      selectedReport.value = fullReport
    }

    previewDialogVisible.value = true
  } catch (err: any) {
    ElMessage.error(err.message || '載入報告詳情失敗')
  }
}

const handleDownloadReport = async (report: ReportListItem | ReportResponse | null) => {
  if (!report) return

  try {
    const fileName = `${report.report_title || 'report'}_${Date.now()}.${report.file_format || 'xlsx'}`
    await reportApi.downloadReport(report.id, fileName)
    ElMessage.success('報告下載開始')
  } catch (err: any) {
    ElMessage.error(err.message || '下載報告失敗')
  }
}

const handleShowEmailDialog = (report: ReportListItem | ReportResponse | null) => {
  if (!report) return

  selectedReport.value = 'report_content' in report
    ? report as ReportResponse
    : null

  // 設定預設主旨
  emailForm.value.subject = `【JGB 智慧物管】${report.report_title}`
  emailForm.value.message = '您好，\n\n附件為客戶健檢報告，請查收。\n\n祝好\nJGB Smart Property'
  emailForm.value.recipient_email = ''

  emailDialogVisible.value = true
}

const handleSendEmail = async () => {
  if (!emailFormRef.value || !selectedReport.value) return

  await emailFormRef.value.validate(async (valid) => {
    if (!valid) return

    sending.value = true

    try {
      const response = await reportApi.sendReportEmail({
        report_id: selectedReport.value!.id,
        recipient_email: emailForm.value.recipient_email,
        subject: emailForm.value.subject || undefined,
        message: emailForm.value.message || undefined
      })

      if (response.success) {
        ElMessage.success('Email 發送成功')
        emailDialogVisible.value = false
        emailFormRef.value?.resetFields()
      } else {
        ElMessage.warning(response.message || 'Email 發送失敗')
      }
    } catch (err: any) {
      ElMessage.error(err.message || '發送 Email 失敗')
    } finally {
      sending.value = false
    }
  })
}

const handleDeleteReport = async (report: ReportListItem) => {
  try {
    await ElMessageBox.confirm(
      `確定要刪除報告「${report.report_title}」嗎？此操作無法恢復。`,
      '刪除確認',
      {
        confirmButtonText: '確定刪除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await reportApi.deleteReport(report.id)
    ElMessage.success('報告已刪除')
    emit('reportDeleted', report.id)

    // 重新載入列表
    await loadReports()
  } catch (err: any) {
    if (err !== 'cancel') {
      ElMessage.error(err.message || '刪除報告失敗')
    }
  }
}

// Lifecycle
onMounted(() => {
  if (props.autoLoad) {
    loadReports()
  }
})

watch(
  () => props.customerId,
  () => {
    if (props.autoLoad) {
      loadReports()
    }
  }
)

// Expose methods
defineExpose({
  loadReports,
  generateReport: handleGenerateReport
})
</script>

<style scoped lang="scss">
.health-check-report {
  .report-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h3 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
    }
  }

  .loading-container {
    padding: 20px 0;
  }

  .error-alert {
    margin-bottom: 20px;
  }

  .report-content {
    .el-table {
      margin-bottom: 20px;

      ::v-deep(.el-button-group) {
        display: flex;
      }
    }

    .pagination {
      display: flex;
      justify-content: flex-end;
      margin-top: 20px;
    }
  }

  .preview-dialog {
    .report-preview {
      .preview-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        padding-bottom: 16px;
        border-bottom: 2px solid var(--el-border-color-light);

        h2 {
          margin: 0;
          font-size: 24px;
          color: var(--el-text-color-primary);
        }
      }

      .preview-content {
        .preview-section {
          margin-bottom: 24px;

          h3 {
            margin: 0 0 16px 0;
            font-size: 16px;
            font-weight: 600;
            color: var(--el-text-color-primary);
          }
        }

        .aa-reasons-list {
          margin: 0;
          padding-left: 20px;

          li {
            margin-bottom: 8px;
            line-height: 1.6;
            color: var(--el-text-color-regular);
          }
        }

        .answer-text {
          white-space: pre-wrap;
          line-height: 1.6;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .health-check-report {
    .report-header {
      flex-direction: column;
      align-items: stretch;
      gap: 12px;

      h3 {
        text-align: center;
      }

      .el-button {
        width: 100%;
      }
    }

    .el-table {
      ::v-deep(.el-button-group) {
        flex-direction: column;

        .el-button {
          border-radius: 0;

          &:first-child {
            border-top-left-radius: var(--el-border-radius-base);
            border-top-right-radius: var(--el-border-radius-base);
          }

          &:last-child {
            border-bottom-left-radius: var(--el-border-radius-base);
            border-bottom-right-radius: var(--el-border-radius-base);
          }
        }
      }
    }

    .preview-dialog {
      ::v-deep(.el-dialog) {
        width: 95% !important;
      }
    }
  }
}
</style>
