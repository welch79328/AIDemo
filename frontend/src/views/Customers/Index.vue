<template>
  <div class="customers-page">
    <!-- 搜尋與操作列 -->
    <el-card class="search-card" shadow="never">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜尋公司名稱、聯絡人、電話"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterStatus" placeholder="客戶狀態" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="已接觸" value="contacted" />
            <el-option label="已排程一訪" value="first_visit_scheduled" />
            <el-option label="已完成一訪" value="first_visit_done" />
            <el-option label="已排程二訪" value="second_visit_scheduled" />
            <el-option label="已完成二訪" value="second_visit_done" />
            <el-option label="洽談中" value="negotiating" />
            <el-option label="已簽約" value="signed" />
            <el-option label="未成交" value="lost" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterStage" placeholder="經營階段" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="個人戶" value="individual" />
            <el-option label="準備成立公司" value="preparing_company" />
            <el-option label="剛成立公司" value="new_company" />
            <el-option label="數位升級" value="scaling_up" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterAA" placeholder="AA客戶" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="是" :value="true" />
            <el-option label="否" :value="false" />
          </el-select>
        </el-col>
        <el-col :span="6" style="text-align: right">
          <el-button type="success" @click="handleImportLeads" :icon="Upload">匯入名單</el-button>
          <el-button type="primary" @click="handleCreate" :icon="Plus">新增客戶</el-button>
          <el-button @click="handleRefresh" :icon="Refresh">重新整理</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 統計卡片 -->
    <el-row :gutter="20" class="stats-row" v-if="statistics">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="總客戶數" :value="statistics.total_customers">
            <template #prefix>
              <el-icon style="vertical-align: middle"><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="AA 客戶" :value="statistics.aa_customers">
            <template #prefix>
              <el-icon style="vertical-align: middle; color: #f56c6c"><Star /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic
            title="平均成熟度"
            :value="statistics.average_maturity_score || 0"
            :precision="1"
            suffix="分"
          />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="已簽約客戶" :value="statistics.by_status?.signed || 0" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 客戶列表表格 -->
    <el-card class="table-card" shadow="never">
      <el-table
        :data="customerStore.customers"
        v-loading="customerStore.loading"
        stripe
        style="width: 100%"
        @row-click="handleRowClick"
      >
        <el-table-column prop="company_name" label="公司名稱" min-width="180" />
        <el-table-column prop="contact_person" label="聯絡人" width="100" />
        <el-table-column prop="contact_phone" label="聯絡電話" width="130" />
        <el-table-column label="經營階段" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.customer_stage" size="small" :type="getStageTagType(row.customer_stage)">
              {{ getStageLabel(row.customer_stage) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="客戶狀態" width="120">
          <template #default="{ row }">
            <el-tag size="small" :type="getStatusTagType(row.current_status)">
              {{ getStatusLabel(row.current_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="AA客戶" width="80" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.is_aa_customer" style="color: #f56c6c; font-size: 18px">
              <Star />
            </el-icon>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="成熟度" width="90" align="center">
          <template #default="{ row }">
            <span v-if="row.maturity_score !== null">{{ row.maturity_score }} 分</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="建立時間" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="handleEdit(row)">
              編輯
            </el-button>
            <el-button link type="info" size="small" @click.stop="handleView(row)">
              查看
            </el-button>
            <el-button link type="danger" size="small" @click.stop="handleDelete(row)">
              刪除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分頁 -->
      <el-pagination
        v-model:current-page="customerStore.page"
        v-model:page-size="customerStore.limit"
        :page-sizes="[10, 20, 50, 100]"
        :total="customerStore.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        class="pagination"
      />
    </el-card>

    <!-- 新增/編輯對話框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="公司名稱" prop="company_name">
          <el-input v-model="formData.company_name" placeholder="請輸入公司名稱" />
        </el-form-item>
        <el-form-item label="聯絡人" prop="contact_person">
          <el-input v-model="formData.contact_person" placeholder="請輸入聯絡人" />
        </el-form-item>
        <el-form-item label="聯絡電話" prop="contact_phone">
          <el-input v-model="formData.contact_phone" placeholder="請輸入聯絡電話" />
        </el-form-item>
        <el-form-item label="聯絡信箱" prop="contact_email">
          <el-input v-model="formData.contact_email" placeholder="請輸入聯絡信箱" type="email" />
        </el-form-item>
        <el-form-item label="公司網站" prop="website">
          <el-input v-model="formData.website" placeholder="請輸入公司網站" />
        </el-form-item>
        <el-form-item label="經營階段" prop="customer_stage">
          <el-select v-model="formData.customer_stage" placeholder="請選擇經營階段">
            <el-option label="個人戶" value="individual" />
            <el-option label="準備成立公司" value="preparing_company" />
            <el-option label="剛成立公司" value="new_company" />
            <el-option label="數位升級" value="scaling_up" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="customerStore.loading">
          確定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { Search, Plus, Refresh, User, Star, Upload } from '@element-plus/icons-vue'
import { useCustomerStore } from '@/stores/customer'
import type { CustomerListItem, CustomerCreateRequest, CustomerUpdateRequest } from '@/api/customer'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const customerStore = useCustomerStore()

// 搜尋與篩選
const searchQuery = ref('')
const filterStatus = ref('')
const filterStage = ref('')
const filterAA = ref<boolean | ''>('')

// 統計資料
const statistics = ref(null)

// 對話框
const dialogVisible = ref(false)
const dialogTitle = ref('新增客戶')
const dialogMode = ref<'create' | 'edit'>('create')
const currentEditId = ref('')

// 表單
const formRef = ref<FormInstance>()
const formData = ref<CustomerCreateRequest & CustomerUpdateRequest>({
  company_name: '',
  contact_person: '',
  contact_phone: '',
  contact_email: '',
  website: '',
  customer_stage: undefined
})

const formRules: FormRules = {
  company_name: [
    { required: true, message: '請輸入公司名稱', trigger: 'blur' }
  ],
  contact_email: [
    { type: 'email', message: '請輸入正確的信箱格式', trigger: 'blur' }
  ]
}

// 載入資料
onMounted(async () => {
  await loadData()
  await loadStatistics()
})

async function loadData() {
  const params: any = {}
  if (searchQuery.value) params.search = searchQuery.value
  if (filterStatus.value) params.status = filterStatus.value
  if (filterStage.value) params.stage = filterStage.value
  if (filterAA.value !== '') params.is_aa = filterAA.value

  await customerStore.fetchCustomers(params)
}

async function loadStatistics() {
  statistics.value = await customerStore.fetchStatistics() as any
}

// 搜尋
function handleSearch() {
  customerStore.setPage(1)
  loadData()
}

// 重新整理
async function handleRefresh() {
  searchQuery.value = ''
  filterStatus.value = ''
  filterStage.value = ''
  filterAA.value = ''
  customerStore.setPage(1)
  await loadData()
  await loadStatistics()
}

// 分頁
function handleSizeChange(size: number) {
  customerStore.setLimit(size)
  loadData()
}

function handlePageChange(page: number) {
  customerStore.setPage(page)
  loadData()
}

// 新增客戶
function handleCreate() {
  dialogMode.value = 'create'
  dialogTitle.value = '新增客戶'
  formData.value = {
    company_name: '',
    contact_person: '',
    contact_phone: '',
    contact_email: '',
    website: '',
    customer_stage: undefined
  }
  dialogVisible.value = true
}

// 編輯客戶
function handleEdit(row: CustomerListItem) {
  dialogMode.value = 'edit'
  dialogTitle.value = '編輯客戶'
  currentEditId.value = row.id
  formData.value = {
    company_name: row.company_name,
    contact_person: row.contact_person || '',
    contact_phone: row.contact_phone || '',
    customer_stage: row.customer_stage
  }
  dialogVisible.value = true
}

// 查看客戶詳情
function handleView(row: CustomerListItem) {
  router.push(`/customers/${row.id}`)
}

// 點擊行
function handleRowClick(row: CustomerListItem) {
  handleView(row)
}

// 刪除客戶
async function handleDelete(row: CustomerListItem) {
  try {
    await ElMessageBox.confirm(
      `確定要刪除客戶「${row.company_name}」嗎？`,
      '刪除確認',
      {
        confirmButtonText: '確定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await customerStore.deleteCustomer(row.id)
    await loadStatistics()
  } catch (error) {
    // 取消刪除
  }
}

// 提交表單
async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (dialogMode.value === 'create') {
          await customerStore.createCustomer(formData.value)
        } else {
          await customerStore.updateCustomer(currentEditId.value, formData.value)
        }
        dialogVisible.value = false
        await loadStatistics()
      } catch (error) {
        // 錯誤已在 store 中處理
      }
    }
  })
}

// 關閉對話框
function handleDialogClose() {
  formRef.value?.resetFields()
}

// 匯入名單
function handleImportLeads() {
  router.push('/leads/import')
}

// 輔助函數
function getStageLabel(stage: string): string {
  const labels: Record<string, string> = {
    individual: '個人戶',
    preparing_company: '準備成立',
    new_company: '剛成立',
    scaling_up: '數位升級'
  }
  return labels[stage] || stage
}

function getStageTagType(stage: string): string {
  const types: Record<string, any> = {
    individual: '',
    preparing_company: 'info',
    new_company: 'success',
    scaling_up: 'warning'
  }
  return types[stage] || ''
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    contacted: '已接觸',
    first_visit_scheduled: '已排程一訪',
    first_visit_done: '已完成一訪',
    second_visit_scheduled: '已排程二訪',
    second_visit_done: '已完成二訪',
    negotiating: '洽談中',
    signed: '已簽約',
    lost: '未成交'
  }
  return labels[status] || status
}

function getStatusTagType(status: string): string {
  const types: Record<string, any> = {
    contacted: 'info',
    first_visit_scheduled: '',
    first_visit_done: 'success',
    second_visit_scheduled: '',
    second_visit_done: 'success',
    negotiating: 'warning',
    signed: 'success',
    lost: 'danger'
  }
  return types[status] || ''
}

function formatDateTime(dateString: string): string {
  return new Date(dateString).toLocaleString('zh-TW')
}
</script>

<style scoped>
.customers-page {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>
