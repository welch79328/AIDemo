<template>
  <div class="leads-import-container">
    <el-card class="upload-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2>Excel 名單導入</h2>
          <el-button type="primary" :icon="Download" @click="downloadTemplate">
            下載範本
          </el-button>
        </div>
      </template>

      <!-- 檔案上傳區 -->
      <FileUpload
        ref="fileUploadRef"
        accept=".xlsx,.xls"
        :max-size="10"
        :multiple="false"
        @upload="handleUpload"
        @error="handleUploadError"
      >
        <template #tip>
          <span>僅支援 Excel 檔案（.xlsx, .xls），檔案大小不超過 10MB</span>
        </template>
      </FileUpload>

      <!-- 導入選項 -->
      <div class="import-options">
        <h3>導入選項</h3>
        <el-form :model="importOptions" label-width="140px">
          <el-form-item label="重複資料處理">
            <el-radio-group v-model="importOptions.duplicate_strategy">
              <el-radio :label="DuplicateStrategy.SKIP">跳過重複資料</el-radio>
              <el-radio :label="DuplicateStrategy.UPDATE">更新現有資料</el-radio>
              <el-radio :label="DuplicateStrategy.KEEP_BOTH">全部保留</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="跳過資料驗證">
            <el-switch v-model="importOptions.skip_validation" />
            <span class="option-hint">（不建議，可能導入無效資料）</span>
          </el-form-item>
        </el-form>
      </div>

      <!-- 上傳按鈕 -->
      <div class="upload-actions">
        <el-button
          type="primary"
          size="large"
          :loading="uploading"
          :disabled="uploading"
          @click="startUpload"
        >
          {{ uploading ? '上傳中...' : '開始導入' }}
        </el-button>
        <el-button size="large" @click="resetUpload" :disabled="uploading">
          重置
        </el-button>
      </div>
    </el-card>

    <!-- 導入結果 -->
    <el-card v-if="importResult" class="result-card" shadow="hover">
      <template #header>
        <h2>導入結果</h2>
      </template>

      <el-result
        :icon="resultIcon"
        :title="resultTitle"
        :sub-title="resultSubTitle"
      >
        <template #extra>
          <div class="result-stats">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="總筆數">
                {{ importResult.total_rows }}
              </el-descriptions-item>
              <el-descriptions-item label="成功匯入">
                <el-tag type="success">{{ importResult.successful_imports }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="匯入失敗">
                <el-tag type="danger">{{ importResult.failed_imports }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="重複資料">
                <el-tag type="warning">{{ importResult.duplicate_count }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>

            <!-- 錯誤報告 -->
            <div v-if="importResult.failed_imports > 0" class="error-actions">
              <el-button
                type="warning"
                :icon="Download"
                @click="showErrorDialog = true"
              >
                查看錯誤詳情
              </el-button>
            </div>

            <!-- 重複資料處理 -->
            <div v-if="importResult.duplicate_count > 0 && importResult.duplicates" class="duplicate-actions">
              <el-button
                type="primary"
                :icon="View"
                @click="showDuplicateDialog = true"
              >
                查看重複資料 ({{ importResult.duplicate_count }})
              </el-button>
            </div>
          </div>
        </template>
      </el-result>
    </el-card>

    <!-- 統計圖表 -->
    <el-card class="statistics-card" shadow="hover">
      <template #header>
        <h2>導入統計</h2>
      </template>

      <v-chart
        v-if="chartData.xAxis.length > 0"
        class="chart"
        :option="chartOption"
        autoresize
      />
      <el-empty v-else description="暫無統計資料" />
    </el-card>

    <!-- 導入歷史 -->
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2>導入歷史</h2>
          <el-select
            v-model="historyFilter.status"
            placeholder="篩選狀態"
            clearable
            style="width: 150px"
            @change="loadHistory"
          >
            <el-option label="全部" value="" />
            <el-option label="處理中" :value="ImportBatchStatus.PROCESSING" />
            <el-option label="完成" :value="ImportBatchStatus.COMPLETED" />
            <el-option label="失敗" :value="ImportBatchStatus.FAILED" />
            <el-option label="部分成功" :value="ImportBatchStatus.PARTIAL_SUCCESS" />
          </el-select>
        </div>
      </template>

      <el-table
        v-loading="loadingHistory"
        :data="historyData"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="file_name" label="檔案名稱" min-width="200" />
        <el-table-column label="狀態" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_rows" label="總筆數" width="100" align="center" />
        <el-table-column prop="successful_imports" label="成功" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="success" size="small">{{ row.successful_imports }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="failed_imports" label="失敗" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.failed_imports > 0" type="danger" size="small">
              {{ row.failed_imports }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="duplicate_count" label="重複" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.duplicate_count > 0" type="warning" size="small">
              {{ row.duplicate_count }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="導入時間" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.failed_imports > 0"
              type="warning"
              size="small"
              :icon="View"
              @click="viewBatchDetails(row)"
            >
              詳情
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="deleteBatch(row.id)"
            >
              刪除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分頁 -->
      <el-pagination
        v-model:current-page="historyPagination.page"
        v-model:page-size="historyPagination.limit"
        :total="historyPagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="loadHistory"
        @size-change="loadHistory"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 錯誤詳情對話框 -->
    <el-dialog
      v-model="showErrorDialog"
      title="錯誤詳情"
      width="70%"
      :close-on-click-modal="false"
    >
      <el-table
        v-if="importResult?.errors"
        :data="importResult.errors"
        stripe
        border
        max-height="400"
      >
        <el-table-column prop="row" label="行號" width="80" />
        <el-table-column prop="field" label="欄位" width="150" />
        <el-table-column prop="message" label="錯誤訊息" />
      </el-table>
      <template #footer>
        <el-button @click="showErrorDialog = false">關閉</el-button>
      </template>
    </el-dialog>

    <!-- 重複資料對話框 -->
    <el-dialog
      v-model="showDuplicateDialog"
      title="重複資料"
      width="80%"
      :close-on-click-modal="false"
    >
      <el-table
        v-if="importResult?.duplicates"
        :data="importResult.duplicates"
        stripe
        border
        max-height="400"
      >
        <el-table-column prop="row_number" label="行號" width="80" />
        <el-table-column prop="reason" label="重複原因" width="200" />
        <el-table-column label="資料內容">
          <template #default="{ row }">
            <pre>{{ JSON.stringify(row.data, null, 2) }}</pre>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="showDuplicateDialog = false">關閉</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, View, Delete } from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import type { EChartsOption } from 'echarts'
import FileUpload from '@/components/common/FileUpload.vue'
import {
  leadApi,
  DuplicateStrategy,
  ImportBatchStatus,
  type ImportOptions,
  type LeadImportResponse,
  type ImportBatchSummary
} from '@/api/lead'
import dayjs from 'dayjs'

// 註冊 ECharts 組件
use([
  CanvasRenderer,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// State
const fileUploadRef = ref<InstanceType<typeof FileUpload>>()
const uploading = ref(false)
const importResult = ref<LeadImportResponse | null>(null)

const importOptions = reactive<ImportOptions>({
  duplicate_strategy: DuplicateStrategy.SKIP,
  skip_validation: false
})

// 歷史記錄
const loadingHistory = ref(false)
const historyData = ref<ImportBatchSummary[]>([])
const historyFilter = reactive({
  status: '' as ImportBatchStatus | ''
})
const historyPagination = reactive({
  page: 1,
  limit: 20,
  total: 0,
  total_pages: 0
})

// 對話框
const showErrorDialog = ref(false)
const showDuplicateDialog = ref(false)

// 圖表數據
const chartData = reactive({
  xAxis: [] as string[],
  successful: [] as number[],
  failed: [] as number[],
  duplicates: [] as number[]
})

// Computed
const resultIcon = computed(() => {
  if (!importResult.value) return 'success'
  if (importResult.value.failed_imports === 0) return 'success'
  if (importResult.value.successful_imports === 0) return 'error'
  return 'warning'
})

const resultTitle = computed(() => {
  if (!importResult.value) return '導入成功'
  if (importResult.value.failed_imports === 0) return '導入成功'
  if (importResult.value.successful_imports === 0) return '導入失敗'
  return '部分成功'
})

const resultSubTitle = computed(() => {
  if (!importResult.value) return ''
  return `成功 ${importResult.value.successful_imports} 筆，失敗 ${importResult.value.failed_imports} 筆`
})

const chartOption = computed<EChartsOption>(() => ({
  title: {
    text: '最近 10 次導入統計',
    left: 'center',
    textStyle: {
      fontSize: 16,
      fontWeight: 600
    }
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    },
    formatter: (params: any) => {
      const date = params[0].axisValue
      let result = `<strong>${date}</strong><br/>`
      params.forEach((item: any) => {
        result += `${item.marker} ${item.seriesName}: ${item.value}<br/>`
      })
      return result
    }
  },
  legend: {
    data: ['成功', '失敗', '重複'],
    top: 35
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: 80,
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: chartData.xAxis,
    axisLabel: {
      rotate: 45,
      interval: 0
    }
  },
  yAxis: {
    type: 'value',
    name: '筆數',
    minInterval: 1
  },
  series: [
    {
      name: '成功',
      type: 'bar',
      stack: 'total',
      data: chartData.successful,
      itemStyle: {
        color: '#67C23A'
      },
      emphasis: {
        focus: 'series'
      }
    },
    {
      name: '失敗',
      type: 'bar',
      stack: 'total',
      data: chartData.failed,
      itemStyle: {
        color: '#F56C6C'
      },
      emphasis: {
        focus: 'series'
      }
    },
    {
      name: '重複',
      type: 'bar',
      stack: 'total',
      data: chartData.duplicates,
      itemStyle: {
        color: '#E6A23C'
      },
      emphasis: {
        focus: 'series'
      }
    }
  ]
}))

// Methods

/**
 * 開始上傳
 */
function startUpload() {
  if (fileUploadRef.value) {
    fileUploadRef.value.triggerUpload()
  }
}

/**
 * 處理檔案上傳
 */
async function handleUpload(files: File[]) {
  if (files.length === 0) {
    ElMessage.warning('請選擇檔案')
    return
  }

  const file = files[0]
  uploading.value = true
  importResult.value = null

  try {
    const result = await leadApi.importLeads(
      file,
      importOptions,
      (progress) => {
        if (fileUploadRef.value) {
          fileUploadRef.value.updateProgress(
            progress.percentage || 0,
            `上傳中... ${progress.percentage}%`
          )
        }
      }
    )

    importResult.value = result

    if (fileUploadRef.value) {
      fileUploadRef.value.updateProgress(100, '導入完成')
    }

    if (result.failed_imports === 0) {
      ElMessage.success(`成功導入 ${result.successful_imports} 筆資料`)
    } else if (result.successful_imports === 0) {
      ElMessage.error('導入失敗，請檢查錯誤詳情')
    } else {
      ElMessage.warning(`部分成功：${result.successful_imports} 筆成功，${result.failed_imports} 筆失敗`)
    }

    // 重新載入歷史記錄
    loadHistory()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '導入失敗')
    if (fileUploadRef.value) {
      fileUploadRef.value.updateProgress(-1, '導入失敗')
    }
  } finally {
    uploading.value = false
  }
}

/**
 * 處理上傳錯誤
 */
function handleUploadError(message: string) {
  ElMessage.error(message)
}

/**
 * 重置上傳
 */
function resetUpload() {
  if (fileUploadRef.value) {
    fileUploadRef.value.clearFiles()
  }
  importResult.value = null
  importOptions.duplicate_strategy = DuplicateStrategy.SKIP
  importOptions.skip_validation = false
}

/**
 * 下載範本
 */
function downloadTemplate() {
  // TODO: 實作範本下載
  ElMessage.info('範本下載功能待實作')
}

/**
 * 載入導入歷史
 */
async function loadHistory() {
  loadingHistory.value = true

  try {
    const result = await leadApi.getImportHistory({
      page: historyPagination.page,
      limit: historyPagination.limit,
      status: historyFilter.status || undefined
    })

    historyData.value = result.batches
    historyPagination.total = result.total
    historyPagination.total_pages = result.total_pages

    // 更新圖表數據（最近 10 次）
    updateChartData(result.batches.slice(0, 10))
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '載入歷史記錄失敗')
  } finally {
    loadingHistory.value = false
  }
}

/**
 * 更新圖表數據
 */
function updateChartData(batches: ImportBatchSummary[]) {
  // 反轉陣列，使最早的在左邊
  const reversedBatches = [...batches].reverse()

  chartData.xAxis = reversedBatches.map(b =>
    dayjs(b.created_at).format('MM-DD HH:mm')
  )
  chartData.successful = reversedBatches.map(b => b.successful_imports)
  chartData.failed = reversedBatches.map(b => b.failed_imports)
  chartData.duplicates = reversedBatches.map(b => b.duplicate_count)
}

/**
 * 查看批次詳情
 */
function viewBatchDetails(batch: ImportBatchSummary) {
  // TODO: 實作詳情對話框
  ElMessage.info('詳情功能待實作')
}

/**
 * 刪除批次
 */
async function deleteBatch(batchId: string) {
  try {
    await ElMessageBox.confirm(
      '確定要刪除此導入記錄嗎？此操作無法復原。',
      '警告',
      {
        confirmButtonText: '確定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await leadApi.deleteImportBatch(batchId)
    ElMessage.success('刪除成功')
    loadHistory()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '刪除失敗')
    }
  }
}

/**
 * 取得狀態標籤類型
 */
function getStatusType(status: ImportBatchStatus): 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case ImportBatchStatus.COMPLETED:
      return 'success'
    case ImportBatchStatus.PROCESSING:
      return 'info'
    case ImportBatchStatus.FAILED:
      return 'danger'
    case ImportBatchStatus.PARTIAL_SUCCESS:
      return 'warning'
    default:
      return 'info'
  }
}

/**
 * 取得狀態文字
 */
function getStatusText(status: ImportBatchStatus): string {
  switch (status) {
    case ImportBatchStatus.COMPLETED:
      return '完成'
    case ImportBatchStatus.PROCESSING:
      return '處理中'
    case ImportBatchStatus.FAILED:
      return '失敗'
    case ImportBatchStatus.PARTIAL_SUCCESS:
      return '部分成功'
    default:
      return '未知'
  }
}

/**
 * 格式化日期時間
 */
function formatDateTime(dateTime: string): string {
  return dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss')
}

// Lifecycle
onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.leads-import-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.upload-card,
.result-card,
.statistics-card,
.history-card {
  margin-bottom: 20px;
}

.chart {
  width: 100%;
  height: 400px;
}

.import-options {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.import-options h3 {
  margin-bottom: 20px;
  font-size: 16px;
  font-weight: 600;
}

.option-hint {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.upload-actions {
  margin-top: 30px;
  text-align: center;
}

.result-stats {
  margin-top: 20px;
}

.error-actions,
.duplicate-actions {
  margin-top: 20px;
  text-align: center;
}

pre {
  margin: 0;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
}
</style>
