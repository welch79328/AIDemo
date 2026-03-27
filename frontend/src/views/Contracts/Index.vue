<template>
  <div class="contracts-page">
    <!-- 頁面標題 -->
    <div class="page-header">
      <h2>簽約管理</h2>
      <el-button type="primary" @click="handleCreate">新增簽約記錄</el-button>
    </div>

    <!-- 統計卡片 -->
    <el-row :gutter="20" class="statistics-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #409eff">
              <el-icon :size="30"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">總簽約數</div>
              <div class="stat-value">{{ statistics?.total_contracts || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #67c23a">
              <el-icon :size="30"><SuccessFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">導入成功</div>
              <div class="stat-value">{{ statistics?.onboarding_success_count || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #e6a23c">
              <el-icon :size="30"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">導入成功率</div>
              <div class="stat-value">{{ statistics?.onboarding_success_rate || 0 }}%</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #f56c6c">
              <el-icon :size="30"><Money /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">總月費金額</div>
              <div class="stat-value">{{ formatMoney(statistics?.total_monthly_value) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 篩選區域 -->
    <el-card shadow="never" class="filter-card">
      <el-form :inline="true">
        <el-form-item label="客戶">
          <el-select
            v-model="filterParams.customer_id"
            clearable
            filterable
            placeholder="選擇客戶"
            style="width: 200px"
            @change="handleFilter"
          >
            <el-option
              v-for="customer in customers"
              :key="customer.id"
              :label="customer.company_name"
              :value="customer.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="合約類型">
          <el-select
            v-model="filterParams.contract_type"
            clearable
            placeholder="選擇合約類型"
            style="width: 150px"
            @change="handleFilter"
          >
            <el-option label="包租" value="package_rental" />
            <el-option label="代管" value="property_mgmt" />
            <el-option label="代租" value="sublease" />
            <el-option label="混合" value="hybrid" />
          </el-select>
        </el-form-item>

        <el-form-item label="導入狀態">
          <el-select
            v-model="filterParams.onboarding_success"
            clearable
            placeholder="選擇導入狀態"
            style="width: 150px"
            @change="handleFilter"
          >
            <el-option label="導入成功" :value="true" />
            <el-option label="尚未完成" :value="false" />
          </el-select>
        </el-form-item>

        <el-form-item label="簽約日期">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="開始日期"
            end-placeholder="結束日期"
            value-format="YYYY-MM-DD"
            style="width: 300px"
            @change="handleDateRangeChange"
          />
        </el-form-item>

        <el-form-item>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 資料表格 -->
    <el-card shadow="never">
      <el-table
        :data="contractStore.contracts"
        v-loading="contractStore.loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="customer_id" label="客戶名稱" width="200">
          <template #default="{ row }">
            {{ getCustomerName(row.customer_id) }}
          </template>
        </el-table-column>

        <el-table-column prop="contract_type" label="合約類型" width="120">
          <template #default="{ row }">
            <el-tag :type="getContractTypeTagType(row.contract_type)">
              {{ getContractTypeLabel(row.contract_type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="contract_date" label="簽約日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.contract_date) }}
          </template>
        </el-table-column>

        <el-table-column prop="property_count" label="物件數" width="100" align="center">
          <template #default="{ row }">
            {{ row.property_count || '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="monthly_value" label="月費金額" width="120" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.monthly_value) }}
          </template>
        </el-table-column>

        <el-table-column prop="onboarding_success" label="導入狀態" width="100">
          <template #default="{ row }">
            <el-tag :type="row.onboarding_success ? 'success' : 'warning'">
              {{ row.onboarding_success ? '已完成' : '進行中' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="建立時間" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" text @click="handleEdit(row)">
              編輯
            </el-button>
            <el-button type="danger" size="small" text @click="handleDelete(row)">
              刪除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分頁 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="contractStore.page"
          v-model:page-size="contractStore.limit"
          :page-sizes="[10, 20, 50, 100]"
          :total="contractStore.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新增/編輯對話框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="140px"
      >
        <el-form-item label="客戶" prop="customer_id">
          <el-select
            v-model="formData.customer_id"
            filterable
            placeholder="請選擇客戶"
            style="width: 100%"
          >
            <el-option
              v-for="customer in customers"
              :key="customer.id"
              :label="customer.company_name"
              :value="customer.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="合約類型" prop="contract_type">
          <el-radio-group v-model="formData.contract_type">
            <el-radio label="package_rental">包租</el-radio>
            <el-radio label="property_mgmt">代管</el-radio>
            <el-radio label="sublease">代租</el-radio>
            <el-radio label="hybrid">混合</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="簽約日期" prop="contract_date">
          <el-date-picker
            v-model="formData.contract_date"
            type="date"
            placeholder="選擇簽約日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="物件數量">
          <el-input-number
            v-model="formData.property_count"
            :min="0"
            placeholder="請輸入物件數量"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="月費金額">
          <el-input-number
            v-model="formData.monthly_value"
            :min="0"
            :precision="2"
            placeholder="請輸入月費金額"
            style="width: 100%"
          />
        </el-form-item>

        <el-divider content-position="left">導入 KPI 追蹤</el-divider>

        <el-form-item label="物件上傳率 (%)">
          <el-input-number
            v-model="formData.kpi_property_upload_rate"
            :min="0"
            :max="100"
            :precision="2"
            placeholder="0-100"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="合約建立率 (%)">
          <el-input-number
            v-model="formData.kpi_contract_creation_rate"
            :min="0"
            :max="100"
            :precision="2"
            placeholder="0-100"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="帳單已發送">
          <el-switch v-model="formData.kpi_billing_active" />
        </el-form-item>

        <el-form-item label="金流串接">
          <el-switch v-model="formData.kpi_payment_integrated" />
        </el-form-item>

        <el-form-item label="自動通知">
          <el-switch v-model="formData.kpi_notification_setup" />
        </el-form-item>

        <el-form-item label="SOP 建立">
          <el-switch v-model="formData.kpi_sop_established" />
        </el-form-item>

        <el-divider />

        <el-form-item label="導入成功">
          <el-switch v-model="formData.onboarding_success" />
        </el-form-item>

        <el-form-item label="導入完成日期" v-if="formData.onboarding_success">
          <el-date-picker
            v-model="formData.onboarding_date"
            type="date"
            placeholder="選擇導入完成日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            確定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Document, SuccessFilled, TrendCharts, Money } from '@element-plus/icons-vue'
import { useContractStore } from '@/stores/contract'
import { useCustomerStore } from '@/stores/customer'
import type { ContractListItem, ContractCreateRequest, ContractUpdateRequest } from '@/api/contract'

const contractStore = useContractStore()
const customerStore = useCustomerStore()

// 狀態
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const submitting = ref(false)
const dateRange = ref<[string, string] | null>(null)

// 客戶列表
const customers = computed(() => customerStore.customers)

// 統計資料
const statistics = computed(() => contractStore.statistics)

// 篩選參數
const filterParams = reactive({
  customer_id: undefined as string | undefined,
  contract_type: undefined as string | undefined,
  onboarding_success: undefined as boolean | undefined,
  date_from: undefined as string | undefined,
  date_to: undefined as string | undefined
})

// 表單
const formRef = ref<FormInstance>()
const formData = ref<ContractCreateRequest>({
  customer_id: '',
  contract_date: '',
  contract_type: 'package_rental' as any,
  property_count: undefined,
  monthly_value: undefined,
  kpi_property_upload_rate: undefined,
  kpi_contract_creation_rate: undefined,
  kpi_billing_active: false,
  kpi_payment_integrated: false,
  kpi_notification_setup: false,
  kpi_sop_established: false,
  onboarding_success: false,
  onboarding_date: undefined
})

const formRules: FormRules = {
  customer_id: [
    { required: true, message: '請選擇客戶', trigger: 'change' }
  ],
  contract_type: [
    { required: true, message: '請選擇合約類型', trigger: 'change' }
  ],
  contract_date: [
    { required: true, message: '請選擇簽約日期', trigger: 'change' }
  ]
}

const dialogTitle = computed(() => dialogMode.value === 'create' ? '新增簽約記錄' : '編輯簽約記錄')
const currentEditId = ref<string>('')

// 載入資料
async function loadData() {
  await Promise.all([
    contractStore.fetchContracts(filterParams),
    contractStore.fetchStatistics(),
    customerStore.fetchCustomers()
  ])
}

// 格式化日期
function formatDate(dateString?: string): string {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW')
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

// 格式化金額
function formatMoney(value?: string | number): string {
  if (!value) return '-'
  const num = typeof value === 'string' ? parseFloat(value) : value
  return `NT$ ${num.toLocaleString('zh-TW', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
}

// 取得客戶名稱
function getCustomerName(customerId: string): string {
  const customer = customers.value.find(c => c.id === customerId)
  return customer ? customer.company_name : '未知客戶'
}

// 合約類型標籤
function getContractTypeTagType(type: string): 'primary' | 'success' | 'warning' | 'danger' {
  const types: Record<string, 'primary' | 'success' | 'warning' | 'danger'> = {
    package_rental: 'primary',
    property_mgmt: 'success',
    sublease: 'warning',
    hybrid: 'danger'
  }
  return types[type] || 'primary'
}

function getContractTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    package_rental: '包租',
    property_mgmt: '代管',
    sublease: '代租',
    hybrid: '混合'
  }
  return labels[type] || type
}

// 新增
function handleCreate() {
  dialogMode.value = 'create'
  formData.value = {
    customer_id: '',
    contract_date: '',
    contract_type: 'package_rental' as any,
    property_count: undefined,
    monthly_value: undefined,
    kpi_property_upload_rate: undefined,
    kpi_contract_creation_rate: undefined,
    kpi_billing_active: false,
    kpi_payment_integrated: false,
    kpi_notification_setup: false,
    kpi_sop_established: false,
    onboarding_success: false,
    onboarding_date: undefined
  }
  dialogVisible.value = true
}

// 編輯
function handleEdit(row: ContractListItem) {
  dialogMode.value = 'edit'
  currentEditId.value = row.id
  formData.value = {
    customer_id: row.customer_id,
    contract_date: row.contract_date,
    contract_type: row.contract_type,
    property_count: row.property_count,
    monthly_value: row.monthly_value,
    kpi_property_upload_rate: undefined,
    kpi_contract_creation_rate: undefined,
    kpi_billing_active: false,
    kpi_payment_integrated: false,
    kpi_notification_setup: false,
    kpi_sop_established: false,
    onboarding_success: row.onboarding_success,
    onboarding_date: undefined
  }
  dialogVisible.value = true
}

// 刪除
async function handleDelete(row: ContractListItem) {
  try {
    await ElMessageBox.confirm(
      `確定要刪除這筆簽約記錄嗎?`,
      '刪除確認',
      {
        confirmButtonText: '確定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await contractStore.deleteContract(row.id)
    await loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('刪除簽約記錄失敗:', error)
    }
  }
}

// 提交表單
async function handleSubmit() {
  await formRef.value?.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (dialogMode.value === 'create') {
          await contractStore.createContract(formData.value)
        } else {
          await contractStore.updateContract(currentEditId.value, formData.value as ContractUpdateRequest)
        }
        dialogVisible.value = false
        await loadData()
      } catch (error) {
        console.error('提交表單失敗:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

// 關閉對話框
function handleDialogClose() {
  formRef.value?.resetFields()
}

// 篩選
function handleFilter() {
  contractStore.setPage(1)
  contractStore.fetchContracts(filterParams)
}

// 日期範圍變更
function handleDateRangeChange(value: [string, string] | null) {
  if (value) {
    filterParams.date_from = value[0]
    filterParams.date_to = value[1]
  } else {
    filterParams.date_from = undefined
    filterParams.date_to = undefined
  }
  handleFilter()
}

// 重置篩選
function handleReset() {
  filterParams.customer_id = undefined
  filterParams.contract_type = undefined
  filterParams.onboarding_success = undefined
  filterParams.date_from = undefined
  filterParams.date_to = undefined
  dateRange.value = null
  handleFilter()
}

// 分頁變更
function handlePageChange(page: number) {
  contractStore.setPage(page)
  contractStore.fetchContracts(filterParams)
}

function handleSizeChange(size: number) {
  contractStore.setLimit(size)
  contractStore.fetchContracts(filterParams)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.contracts-page {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      font-size: 24px;
    }
  }

  .statistics-row {
    margin-bottom: 20px;
  }

  .stat-card {
    .stat-content {
      display: flex;
      align-items: center;
      gap: 15px;
    }

    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }

    .stat-info {
      flex: 1;

      .stat-label {
        font-size: 14px;
        color: #909399;
        margin-bottom: 5px;
      }

      .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #303133;
      }
    }
  }

  .filter-card {
    margin-bottom: 20px;
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
