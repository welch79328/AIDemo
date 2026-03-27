<template>
  <div class="dashboard-page">
    <!-- KPI 統計卡片 -->
    <el-row :gutter="20" class="kpi-row">
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card shadow="hover" class="kpi-card">
          <el-statistic title="總客戶數" :value="statistics.total_customers">
            <template #prefix>
              <el-icon class="stat-icon" style="color: #409eff"><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card shadow="hover" class="kpi-card aa-card">
          <el-statistic title="AA 客戶" :value="statistics.aa_customers">
            <template #prefix>
              <el-icon class="stat-icon" style="color: #f56c6c"><StarFilled /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card shadow="hover" class="kpi-card">
          <el-statistic title="本月新增客戶" :value="statistics.new_customers_this_month">
            <template #prefix>
              <el-icon class="stat-icon" style="color: #67c23a"><UserFilled /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card shadow="hover" class="kpi-card">
          <el-statistic title="本月簽約數" :value="statistics.contracts_this_month">
            <template #prefix>
              <el-icon class="stat-icon" style="color: #e6a23c"><DocumentChecked /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二排 KPI -->
    <el-row :gutter="20" class="kpi-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="kpi-card">
          <el-statistic
            title="簽約轉換率"
            :value="statistics.conversion_rate"
            :precision="1"
            suffix="%"
          >
            <template #prefix>
              <el-icon class="stat-icon" style="color: #909399"><TrendCharts /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="kpi-card">
          <el-statistic title="待一訪客戶" :value="statistics.pending_first_visit">
            <template #prefix>
              <el-icon class="stat-icon" style="color: #409eff"><Calendar /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="kpi-card">
          <el-statistic title="待二訪客戶" :value="statistics.pending_second_visit">
            <template #prefix>
              <el-icon class="stat-icon" style="color: #e6a23c"><Calendar /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="kpi-card">
          <el-statistic title="本月拜訪次數" :value="statistics.visits_this_month">
            <template #prefix>
              <el-icon class="stat-icon" style="color: #67c23a"><Location /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 圖表分析區 -->
    <el-row :gutter="20" class="chart-row">
      <!-- 客戶階段分布 -->
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">客戶階段分布</span>
              <el-tag size="small">圓餅圖</el-tag>
            </div>
          </template>
          <v-chart class="chart" :option="stageChartOption" autoresize />
        </el-card>
      </el-col>

      <!-- 客戶狀態分布 -->
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">客戶狀態分布</span>
              <el-tag size="small" type="success">柱狀圖</el-tag>
            </div>
          </template>
          <v-chart class="chart" :option="statusChartOption" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- 月度趨勢圖 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">月度趨勢分析（最近6個月）</span>
              <el-tag size="small" type="warning">折線圖</el-tag>
            </div>
          </template>
          <v-chart class="chart" :option="trendChartOption" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作區 -->
    <el-row :gutter="20" class="action-row">
      <!-- 最近新增客戶 -->
      <el-col :xs="24" :lg="8">
        <el-card shadow="hover" class="action-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">最近新增客戶</span>
              <el-button text type="primary" @click="viewAllCustomers">查看全部</el-button>
            </div>
          </template>
          <el-empty v-if="recentCustomers.length === 0" description="暫無新增客戶" />
          <div v-else class="customer-list">
            <div
              v-for="customer in recentCustomers"
              :key="customer.id"
              class="customer-item"
              @click="viewCustomer(customer.id)"
            >
              <div class="customer-info">
                <div class="customer-name">
                  {{ customer.company_name }}
                  <el-icon v-if="customer.is_aa_customer" style="color: #f56c6c"><StarFilled /></el-icon>
                </div>
                <div class="customer-meta">
                  {{ customer.contact_person }} · {{ formatDate(customer.created_at) }}
                </div>
              </div>
              <el-tag size="small" :type="getStageTagType(customer.customer_stage)">
                {{ getStageLabel(customer.customer_stage) }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 待辦事項 -->
      <el-col :xs="24" :lg="8">
        <el-card shadow="hover" class="action-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">今日待辦事項</span>
              <el-badge :value="todoList.filter(t => !t.completed).length" />
            </div>
          </template>
          <el-empty v-if="todoList.length === 0" description="暫無待辦事項" />
          <div v-else class="todo-list">
            <div
              v-for="todo in todoList"
              :key="todo.id"
              class="todo-item"
              :class="{ completed: todo.completed }"
            >
              <el-checkbox
                :model-value="todo.completed"
                @change="toggleTodo(todo.id)"
              >
                <div class="todo-content">
                  <div class="todo-title">{{ todo.title }}</div>
                  <div class="todo-meta">
                    <el-tag size="small" :type="getPriorityType(todo.priority)">
                      {{ getPriorityLabel(todo.priority) }}
                    </el-tag>
                    <span class="todo-customer">{{ todo.customer_name }}</span>
                  </div>
                </div>
              </el-checkbox>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 需要跟進的客戶 -->
      <el-col :xs="24" :lg="8">
        <el-card shadow="hover" class="action-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">需要跟進</span>
              <el-tag size="small" type="warning">{{ followUpCustomers.length }} 位客戶</el-tag>
            </div>
          </template>
          <el-empty v-if="followUpCustomers.length === 0" description="暫無需要跟進的客戶" />
          <div v-else class="followup-list">
            <div
              v-for="customer in followUpCustomers"
              :key="customer.id"
              class="followup-item"
              @click="viewCustomer(customer.id)"
            >
              <div class="followup-info">
                <div class="followup-name">{{ customer.company_name }}</div>
                <div class="followup-meta">
                  上次聯絡：{{ customer.days_since_contact }} 天前
                </div>
                <div class="followup-action">
                  <el-tag size="small">{{ customer.next_action }}</el-tag>
                </div>
              </div>
              <el-icon class="followup-arrow"><ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User,
  UserFilled,
  StarFilled,
  DocumentChecked,
  TrendCharts,
  Calendar,
  Location,
  ArrowRight
} from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import type { EChartsOption } from 'echarts'
import { dashboardApi } from '@/api/dashboard'
import type {
  DashboardStatistics,
  RecentCustomer,
  TodoItem,
  FollowUpCustomer
} from '@/api/dashboard'
import dayjs from 'dayjs'

// 註冊 ECharts 組件
use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const router = useRouter()

// 統計數據
const statistics = reactive<DashboardStatistics>({
  total_customers: 0,
  aa_customers: 0,
  new_customers_this_month: 0,
  total_contracts: 0,
  contracts_this_month: 0,
  conversion_rate: 0,
  total_visits: 0,
  visits_this_month: 0,
  pending_first_visit: 0,
  pending_second_visit: 0,
  customers_by_status: {
    contacted: 0,
    first_visit_scheduled: 0,
    first_visit_done: 0,
    second_visit_scheduled: 0,
    second_visit_done: 0,
    negotiating: 0,
    signed: 0,
    lost: 0
  },
  customers_by_stage: {
    individual: 0,
    preparing_company: 0,
    new_company: 0,
    scaling_up: 0
  },
  monthly_trends: []
})

const recentCustomers = ref<RecentCustomer[]>([])
const todoList = ref<TodoItem[]>([])
const followUpCustomers = ref<FollowUpCustomer[]>([])

// 客戶階段圓餅圖
const stageChartOption = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} 位客戶 ({d}%)'
  },
  legend: {
    bottom: 10,
    left: 'center'
  },
  series: [
    {
      name: '客戶階段',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 20,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: [
        { value: statistics.customers_by_stage.individual, name: '個人戶' },
        { value: statistics.customers_by_stage.preparing_company, name: '準備成立公司' },
        { value: statistics.customers_by_stage.new_company, name: '剛成立公司' },
        { value: statistics.customers_by_stage.scaling_up, name: '數位升級' }
      ]
    }
  ]
}))

// 客戶狀態柱狀圖
const statusChartOption = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['已接觸', '已排程一訪', '已完成一訪', '已排程二訪', '已完成二訪', '洽談中', '已簽約', '未成交'],
    axisLabel: {
      rotate: 45,
      interval: 0,
      fontSize: 11
    }
  },
  yAxis: {
    type: 'value',
    name: '客戶數',
    minInterval: 1
  },
  series: [
    {
      name: '客戶數',
      type: 'bar',
      data: [
        statistics.customers_by_status.contacted,
        statistics.customers_by_status.first_visit_scheduled,
        statistics.customers_by_status.first_visit_done,
        statistics.customers_by_status.second_visit_scheduled,
        statistics.customers_by_status.second_visit_done,
        statistics.customers_by_status.negotiating,
        statistics.customers_by_status.signed,
        statistics.customers_by_status.lost
      ],
      itemStyle: {
        color: '#409eff',
        borderRadius: [4, 4, 0, 0]
      }
    }
  ]
}))

// 月度趨勢折線圖
const trendChartOption = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['新增客戶', '新增簽約', '拜訪次數'],
    top: 10
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: 60,
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: statistics.monthly_trends.map(t => t.month)
  },
  yAxis: {
    type: 'value',
    name: '數量',
    minInterval: 1
  },
  series: [
    {
      name: '新增客戶',
      type: 'line',
      data: statistics.monthly_trends.map(t => t.new_customers),
      smooth: true,
      itemStyle: { color: '#409eff' },
      areaStyle: { opacity: 0.3 }
    },
    {
      name: '新增簽約',
      type: 'line',
      data: statistics.monthly_trends.map(t => t.new_contracts),
      smooth: true,
      itemStyle: { color: '#67c23a' },
      areaStyle: { opacity: 0.3 }
    },
    {
      name: '拜訪次數',
      type: 'line',
      data: statistics.monthly_trends.map(t => t.visits),
      smooth: true,
      itemStyle: { color: '#e6a23c' },
      areaStyle: { opacity: 0.3 }
    }
  ]
}))

// Methods
async function loadData() {
  try {
    // 載入統計數據
    const stats = await dashboardApi.getStatistics()
    Object.assign(statistics, stats)

    // 載入最近客戶
    recentCustomers.value = await dashboardApi.getRecentCustomers(5)

    // 載入待辦事項
    todoList.value = await dashboardApi.getTodoList()

    // 載入需要跟進的客戶
    followUpCustomers.value = await dashboardApi.getFollowUpCustomers(7)
  } catch (error: any) {
    console.error('載入儀表板數據失敗:', error)
    // ElMessage.error('載入數據失敗')
  }
}

function viewCustomer(customerId: string) {
  router.push(`/customers/${customerId}`)
}

function viewAllCustomers() {
  router.push('/customers')
}

async function toggleTodo(todoId: string) {
  try {
    await dashboardApi.completeTodo(todoId)
    const todo = todoList.value.find(t => t.id === todoId)
    if (todo) {
      todo.completed = !todo.completed
    }
  } catch (error: any) {
    ElMessage.error('操作失敗')
  }
}

function formatDate(dateString: string): string {
  return dayjs(dateString).format('MM/DD')
}

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

function getPriorityLabel(priority: string): string {
  const labels: Record<string, string> = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return labels[priority] || priority
}

function getPriorityType(priority: string): string {
  const types: Record<string, any> = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return types[priority] || 'info'
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard-page {
  padding: 20px;
}

/* KPI 卡片 */
.kpi-row {
  margin-bottom: 20px;
}

.kpi-card {
  transition: all 0.3s;
  cursor: default;
}

.kpi-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.kpi-card.aa-card {
  background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
}

.stat-icon {
  font-size: 24px;
  vertical-align: middle;
}

/* 圖表卡片 */
.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.chart {
  width: 100%;
  height: 350px;
}

/* 快速操作區 */
.action-row {
  margin-bottom: 20px;
}

.action-card {
  height: 100%;
  min-height: 400px;
}

/* 客戶列表 */
.customer-list {
  max-height: 320px;
  overflow-y: auto;
}

.customer-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #ebeef5;
}

.customer-item:hover {
  background-color: #f5f7fa;
  border-color: #409eff;
}

.customer-info {
  flex: 1;
}

.customer-name {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.customer-meta {
  font-size: 12px;
  color: #909399;
}

/* 待辦事項 */
.todo-list {
  max-height: 320px;
  overflow-y: auto;
}

.todo-item {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 4px;
  border: 1px solid #ebeef5;
  transition: all 0.2s;
}

.todo-item:hover {
  background-color: #f5f7fa;
}

.todo-item.completed {
  opacity: 0.6;
}

.todo-item.completed .todo-title {
  text-decoration: line-through;
  color: #909399;
}

.todo-content {
  margin-left: 8px;
}

.todo-title {
  font-size: 14px;
  margin-bottom: 4px;
}

.todo-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.todo-customer {
  color: #606266;
}

/* 跟進客戶 */
.followup-list {
  max-height: 320px;
  overflow-y: auto;
}

.followup-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #ebeef5;
}

.followup-item:hover {
  background-color: #f5f7fa;
  border-color: #e6a23c;
}

.followup-info {
  flex: 1;
}

.followup-name {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.followup-meta {
  font-size: 12px;
  color: #e6a23c;
  margin-bottom: 4px;
}

.followup-action {
  margin-top: 4px;
}

.followup-arrow {
  font-size: 16px;
  color: #909399;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .dashboard-page {
    padding: 10px;
  }

  .kpi-row,
  .chart-row,
  .action-row {
    margin-bottom: 10px;
  }

  .chart {
    height: 280px;
  }

  .action-card {
    min-height: auto;
  }
}
</style>
