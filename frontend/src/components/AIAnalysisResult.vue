<template>
  <div class="ai-analysis-result">
    <!-- 載入狀態 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>載入分析結果中...</p>
    </div>

    <!-- 錯誤狀態 -->
    <el-alert
      v-else-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
    />

    <!-- 分析結果 -->
    <div v-else-if="analysisData" class="analysis-content">
      <!-- 對話摘要 -->
      <el-card v-if="analysisData.summary" class="summary-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Document /></el-icon>
            <span>對話摘要</span>
          </div>
        </template>
        <p class="summary-text">{{ analysisData.summary }}</p>
      </el-card>

      <!-- 評估結果概覽 -->
      <el-row :gutter="20" class="overview-section">
        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>品質評分</span>
              </div>
            </template>
            <div class="score-container">
              <v-chart class="score-chart" :option="qualityScoreOption" autoresize />
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="8">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Histogram /></el-icon>
                <span>問題覆蓋率</span>
              </div>
            </template>
            <div class="coverage-container">
              <el-progress
                type="dashboard"
                :percentage="coveragePercentage"
                :color="getCoverageColor"
              >
                <template #default="{ percentage }">
                  <span class="percentage-value">{{ percentage }}%</span>
                  <span class="percentage-label">已討論</span>
                </template>
              </el-progress>
              <p class="coverage-detail">
                {{ discussedCount }} / {{ totalQuestions }} 個問題
              </p>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="24" :md="8">
          <el-card shadow="hover" :class="aaCardClass">
            <template #header>
              <div class="card-header">
                <el-icon><Medal /></el-icon>
                <span>AA 客戶評估</span>
              </div>
            </template>
            <div class="aa-container">
              <div class="aa-result">
                <el-tag
                  :type="analysisData.is_aa_customer ? 'success' : 'info'"
                  size="large"
                  effect="dark"
                >
                  {{ analysisData.is_aa_customer ? 'AA 客戶' : '非 AA 客戶' }}
                </el-tag>
                <div v-if="analysisData.aa_confidence" class="aa-confidence">
                  信心度: {{ analysisData.aa_confidence }}%
                </div>
              </div>
              <div v-if="analysisData.aa_score" class="aa-score">
                評分: {{ analysisData.aa_score }} 分
              </div>
              <el-collapse v-if="analysisData.aa_reasons && analysisData.aa_reasons.length > 0" class="aa-reasons">
                <el-collapse-item title="判定原因" name="reasons">
                  <ul>
                    <li v-for="(reason, idx) in analysisData.aa_reasons" :key="idx">
                      {{ reason }}
                    </li>
                  </ul>
                </el-collapse-item>
              </el-collapse>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 業務30問匹配結果 -->
      <el-card class="questions-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><List /></el-icon>
            <span>業務30問匹配結果</span>
            <el-radio-group v-model="questionFilter" size="small" class="filter-group">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="discussed">已討論</el-radio-button>
              <el-radio-button label="undiscussed">未討論</el-radio-button>
            </el-radio-group>
          </div>
        </template>

        <el-collapse v-model="activeQuestions" accordion>
          <el-collapse-item
            v-for="question in filteredQuestions"
            :key="question.question_number"
            :name="question.question_number"
          >
            <template #title>
              <div class="question-title">
                <el-tag
                  :type="question.isDiscussed ? 'success' : 'warning'"
                  size="small"
                  effect="plain"
                >
                  {{ question.isDiscussed ? '✓ 已討論' : '✗ 未討論' }}
                </el-tag>
                <span class="question-number">問題 {{ question.question_number }}</span>
                <span class="question-text">{{ question.question }}</span>
                <el-tag v-if="question.confidence" size="small" type="info" class="confidence-tag">
                  信心度: {{ question.confidence }}%
                </el-tag>
              </div>
            </template>

            <!-- 已討論問題的詳細內容 -->
            <div v-if="question.isDiscussed" class="question-detail discussed">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="客戶回答">
                  <div class="answer-content">{{ question.answer }}</div>
                </el-descriptions-item>
                <el-descriptions-item v-if="question.evidence" label="對話片段">
                  <div class="evidence-content">{{ question.evidence }}</div>
                </el-descriptions-item>
                <el-descriptions-item v-if="question.confidence" label="匹配信心度">
                  <el-progress
                    :percentage="question.confidence"
                    :color="getConfidenceColor(question.confidence)"
                  />
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- 未討論問題的建議 -->
            <div v-else class="question-detail undiscussed">
              <el-alert
                title="此問題尚未在對話中討論"
                type="warning"
                :closable="false"
              >
                <template #default>
                  <p><strong>問題內容：</strong>{{ question.question }}</p>
                  <p v-if="question.priority"><strong>優先級：</strong>{{ question.priority }}</p>
                  <p><strong>建議：</strong>建議在後續拜訪時補充此問題，以更全面評估客戶狀況</p>
                </template>
              </el-alert>
            </div>
          </el-collapse-item>
        </el-collapse>

        <el-empty
          v-if="filteredQuestions.length === 0"
          description="無符合條件的問題"
        />
      </el-card>

      <!-- 客戶資訊提取結果 -->
      <el-card
        v-if="analysisData.extracted_info"
        class="extracted-info-card"
        shadow="hover"
      >
        <template #header>
          <div class="card-header">
            <el-icon><User /></el-icon>
            <span>提取的客戶資訊</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item
            v-if="analysisData.extracted_info.company_name"
            label="公司名稱"
          >
            {{ analysisData.extracted_info.company_name }}
          </el-descriptions-item>
          <el-descriptions-item
            v-if="analysisData.extracted_info.property_count"
            label="物件數量"
          >
            {{ analysisData.extracted_info.property_count }}
          </el-descriptions-item>
          <el-descriptions-item
            v-if="analysisData.extracted_info.staff_count"
            label="員工人數"
          >
            {{ analysisData.extracted_info.staff_count }}
          </el-descriptions-item>
          <el-descriptions-item
            v-if="analysisData.extracted_info.business_type"
            label="業務類型"
          >
            {{ analysisData.extracted_info.business_type }}
          </el-descriptions-item>
          <el-descriptions-item
            v-if="analysisData.extracted_info.pain_points && analysisData.extracted_info.pain_points.length > 0"
            label="痛點"
            :span="2"
          >
            <el-tag
              v-for="(point, idx) in analysisData.extracted_info.pain_points"
              :key="idx"
              type="danger"
              effect="plain"
              class="pain-point-tag"
            >
              {{ point }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>

    <!-- 無資料狀態 -->
    <el-empty v-else description="無分析資料" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Loading,
  Document,
  TrendCharts,
  Histogram,
  Medal,
  List,
  User
} from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { GaugeChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent
} from 'echarts/components'
import type { EChartsOption } from 'echarts'

// 註冊 ECharts 組件
use([
  CanvasRenderer,
  GaugeChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent
])

// Props
interface Props {
  analysisId?: string
  analysisData?: AIAnalysisData
  questionnaire?: QuestionnaireQuestion[]
}

// AI 分析資料介面
interface AIAnalysisData {
  id?: string
  interaction_id?: string
  customer_id?: string
  matched_questions: MatchedQuestion[]
  summary?: string
  coverage_rate?: number
  quality_score?: number
  extracted_info?: ExtractedInfo
  is_aa_customer?: boolean
  aa_confidence?: number
  aa_reasons?: string[]
  aa_score?: number
  ai_model_version?: string
  created_at?: string
}

interface MatchedQuestion {
  question_number: number
  question_text: string
  answer: string
  confidence: number
  evidence: string
}

interface ExtractedInfo {
  company_name?: string
  property_count?: number
  staff_count?: number
  business_type?: string
  pain_points: string[]
}

interface QuestionnaireQuestion {
  number: number
  priority: string
  phase: string
  question: string
  options?: string | null
}

interface CombinedQuestion {
  question_number: number
  question: string
  priority?: string
  phase?: string
  isDiscussed: boolean
  answer?: string
  confidence?: number
  evidence?: string
}

const props = withDefaults(defineProps<Props>(), {
  analysisId: undefined,
  analysisData: undefined,
  questionnaire: () => []
})

// Reactive state
const loading = ref(false)
const error = ref<string | null>(null)
const analysisData = ref<AIAnalysisData | null>(null)
const questionFilter = ref<'all' | 'discussed' | 'undiscussed'>('all')
const activeQuestions = ref<number[]>([])

// Computed
const discussedQuestions = computed(() => {
  return analysisData.value?.matched_questions || []
})

const discussedCount = computed(() => discussedQuestions.value.length)

const totalQuestions = computed(() => {
  return props.questionnaire.length || 30
})

const coveragePercentage = computed(() => {
  if (analysisData.value?.coverage_rate !== undefined) {
    return Math.round(analysisData.value.coverage_rate)
  }
  return Math.round((discussedCount.value / totalQuestions.value) * 100)
})

const combinedQuestions = computed<CombinedQuestion[]>(() => {
  const discussed = new Map(
    discussedQuestions.value.map(q => [q.question_number, q])
  )

  return props.questionnaire.map(q => {
    const matchedQ = discussed.get(q.number)
    return {
      question_number: q.number,
      question: q.question,
      priority: q.priority,
      phase: q.phase,
      isDiscussed: !!matchedQ,
      answer: matchedQ?.answer,
      confidence: matchedQ?.confidence,
      evidence: matchedQ?.evidence
    }
  })
})

const filteredQuestions = computed(() => {
  if (questionFilter.value === 'discussed') {
    return combinedQuestions.value.filter(q => q.isDiscussed)
  } else if (questionFilter.value === 'undiscussed') {
    return combinedQuestions.value.filter(q => !q.isDiscussed)
  }
  return combinedQuestions.value
})

const qualityScore = computed(() => {
  return analysisData.value?.quality_score ?? 0
})

const qualityScoreOption = computed<EChartsOption>(() => ({
  series: [
    {
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      splitNumber: 10,
      axisLine: {
        lineStyle: {
          width: 6,
          color: [
            [0.3, '#FF6E76'],
            [0.7, '#FDDD60'],
            [1, '#58D9F9']
          ]
        }
      },
      pointer: {
        icon: 'path://M2090.36389,615.30999 L2090.36389,615.30999 C2091.48372,615.30999 2092.40383,616.194028 2092.44859,617.312956 L2096.90698,728.755929 C2097.05155,732.369577 2094.2393,735.416212 2090.62566,735.56078 C2090.53845,735.564269 2090.45117,735.566014 2090.36389,735.566014 L2090.36389,735.566014 C2086.74736,735.566014 2083.81557,732.63423 2083.81557,729.017692 C2083.81557,728.930412 2083.81732,728.84314 2083.82081,728.755929 L2088.2792,617.312956 C2088.32396,616.194028 2089.24407,615.30999 2090.36389,615.30999 Z',
        length: '75%',
        width: 8,
        offsetCenter: [0, '5%']
      },
      axisTick: {
        length: 8,
        lineStyle: {
          color: 'auto',
          width: 2
        }
      },
      splitLine: {
        length: 10,
        lineStyle: {
          color: 'auto',
          width: 3
        }
      },
      axisLabel: {
        color: '#464646',
        fontSize: 12,
        distance: -40,
        formatter: function (value: number) {
          if (value === 100) {
            return '優秀'
          } else if (value === 75) {
            return '良好'
          } else if (value === 50) {
            return '中等'
          } else if (value === 25) {
            return '差'
          }
          return ''
        }
      },
      title: {
        offsetCenter: [0, '80%'],
        fontSize: 14,
        color: '#464646'
      },
      detail: {
        fontSize: 30,
        offsetCenter: [0, '50%'],
        valueAnimation: true,
        formatter: function (value: number) {
          return Math.round(value) + ' 分'
        },
        color: 'auto'
      },
      data: [
        {
          value: qualityScore.value,
          name: '品質評分'
        }
      ]
    }
  ]
}))

const aaCardClass = computed(() => ({
  'aa-card': true,
  'is-aa': analysisData.value?.is_aa_customer
}))

// Methods
const getCoverageColor = (percentage: number): string => {
  if (percentage < 30) return '#F56C6C'
  if (percentage < 70) return '#E6A23C'
  return '#67C23A'
}

const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 80) return '#67C23A'
  if (confidence >= 60) return '#E6A23C'
  return '#F56C6C'
}

const loadAnalysisData = async () => {
  if (props.analysisData) {
    analysisData.value = props.analysisData
    return
  }

  if (!props.analysisId) {
    return
  }

  loading.value = true
  error.value = null

  try {
    // TODO: 實際呼叫 API 載入分析資料
    // const response = await aiAnalysisApi.getAnalysis(props.analysisId)
    // analysisData.value = response.data

    // 目前使用 props 傳入的資料
    ElMessage.warning('API 尚未實作，請直接傳入 analysisData')
  } catch (err: any) {
    error.value = err.message || '載入分析資料失敗'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadAnalysisData()
})

watch(
  () => props.analysisData,
  (newData) => {
    if (newData) {
      analysisData.value = newData
    }
  },
  { immediate: true }
)

watch(
  () => props.analysisId,
  () => {
    loadAnalysisData()
  }
)
</script>

<style scoped lang="scss">
.ai-analysis-result {
  .loading-container {
    text-align: center;
    padding: 60px 0;

    .el-icon {
      font-size: 48px;
      color: var(--el-color-primary);
      margin-bottom: 16px;
    }

    p {
      color: var(--el-text-color-secondary);
      font-size: 14px;
    }
  }

  .analysis-content {
    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;

      .el-icon {
        font-size: 18px;
      }

      span {
        flex: 1;
        font-weight: 600;
      }

      .filter-group {
        margin-left: auto;
      }
    }
  }

  .summary-card {
    margin-bottom: 20px;

    .summary-text {
      line-height: 1.8;
      color: var(--el-text-color-regular);
      margin: 0;
    }
  }

  .overview-section {
    margin-bottom: 20px;

    .el-card {
      height: 100%;
    }

    .score-container,
    .coverage-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px 0;
    }

    .score-chart {
      width: 100%;
      height: 200px;
    }

    .coverage-container {
      .el-progress {
        margin-bottom: 16px;
      }

      .percentage-value {
        display: block;
        font-size: 28px;
        font-weight: bold;
        color: var(--el-text-color-primary);
      }

      .percentage-label {
        display: block;
        font-size: 12px;
        color: var(--el-text-color-secondary);
        margin-top: 4px;
      }

      .coverage-detail {
        margin: 0;
        color: var(--el-text-color-secondary);
        font-size: 14px;
      }
    }

    .aa-container {
      padding: 20px 0;
      text-align: center;

      .aa-result {
        margin-bottom: 16px;

        .el-tag {
          font-size: 18px;
          padding: 12px 24px;
        }

        .aa-confidence {
          margin-top: 8px;
          font-size: 14px;
          color: var(--el-text-color-secondary);
        }
      }

      .aa-score {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 16px;
        color: var(--el-color-primary);
      }

      .aa-reasons {
        text-align: left;
        margin-top: 16px;

        ul {
          margin: 0;
          padding-left: 20px;

          li {
            margin-bottom: 8px;
            line-height: 1.6;
          }
        }
      }
    }
  }

  .aa-card.is-aa {
    border-color: var(--el-color-success);

    ::v-deep(.el-card__header) {
      background-color: var(--el-color-success-light-9);
    }
  }

  .questions-card {
    margin-bottom: 20px;

    .question-title {
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 1;
      padding-right: 20px;

      .question-number {
        font-weight: 600;
        color: var(--el-text-color-primary);
        min-width: 60px;
      }

      .question-text {
        flex: 1;
        color: var(--el-text-color-regular);
      }

      .confidence-tag {
        margin-left: auto;
      }
    }

    .question-detail {
      margin-top: 12px;

      &.discussed {
        .answer-content,
        .evidence-content {
          line-height: 1.8;
          white-space: pre-wrap;
        }

        .answer-content {
          color: var(--el-text-color-primary);
        }

        .evidence-content {
          color: var(--el-text-color-secondary);
          font-style: italic;
        }
      }

      &.undiscussed {
        p {
          margin: 8px 0;
          line-height: 1.6;

          strong {
            color: var(--el-text-color-primary);
          }
        }
      }
    }
  }

  .extracted-info-card {
    .pain-point-tag {
      margin-right: 8px;
      margin-bottom: 8px;
    }
  }
}

@media (max-width: 768px) {
  .ai-analysis-result {
    .overview-section {
      .el-col {
        margin-bottom: 16px;
      }
    }

    .question-title {
      flex-wrap: wrap;

      .question-text {
        width: 100%;
        order: 3;
        margin-top: 8px;
      }
    }
  }
}
</style>
