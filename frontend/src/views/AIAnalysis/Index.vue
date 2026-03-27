<template>
  <div class="ai-analysis-page">
    <!-- 頁面標題 -->
    <div class="page-header">
      <h2>AI 對談分析</h2>
      <el-tag type="info">客戶健檢表 30 問智能分析</el-tag>
    </div>

    <el-row :gutter="20">
      <!-- 左側：輸入區域 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📝 對談記錄輸入</span>
              <el-button type="primary" size="small" @click="handleAnalyze" :loading="aiStore.loading">
                開始分析
              </el-button>
            </div>
          </template>

          <!-- 文字輸入 -->
          <el-input
            v-model="conversationText"
            type="textarea"
            :rows="20"
            placeholder="請貼上業務與客戶的對談記錄...&#10;&#10;範例：&#10;你&#10; 你們現在大概幾間啊？&#10;業者&#10; 一百多。&#10;你&#10; 那平常租客問題是誰在回？LINE嗎？&#10;業者&#10; 對，LINE為主。"
          />

          <el-divider>或</el-divider>

          <!-- 文件上傳 -->
          <el-upload
            class="upload-demo"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :show-file-list="false"
            accept=".txt"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              將對談記錄文件拖到此處，或<em>點擊上傳</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                僅支援 .txt 文件
              </div>
            </template>
          </el-upload>

          <!-- 範例按鈕 -->
          <div class="example-buttons">
            <el-button size="small" @click="loadExample(1)">載入範例 1 (AA客戶)</el-button>
            <el-button size="small" @click="loadExample(2)">載入範例 2 (小型業者)</el-button>
            <el-button size="small" @click="handleClear">清空</el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右側：分析結果 -->
      <el-col :span="12">
        <!-- 載入中 -->
        <div v-if="aiStore.loading" class="loading-container">
          <el-card shadow="hover">
            <el-skeleton :rows="15" animated />
          </el-card>
        </div>

        <!-- 分析結果 -->
        <div v-else-if="aiStore.analysisResult" class="analysis-results">
          <!-- 操作按鈕 -->
          <el-card shadow="hover" class="action-card">
            <el-button type="success" size="large" @click="showSaveDialog" :icon="DocumentAdd" style="width: 100%">
              儲存為拜訪記錄
            </el-button>
          </el-card>

          <!-- 摘要卡片 -->
          <el-card shadow="hover" class="summary-card">
            <template #header>
              <span>📊 分析摘要</span>
            </template>
            <p class="summary-text">{{ aiStore.analysisResult.summary }}</p>
          </el-card>

          <!-- 客戶資訊卡片 -->
          <el-card shadow="hover" class="info-card" v-if="aiStore.analysisResult.customer_info">
            <template #header>
              <span>👤 客戶基本資訊</span>
            </template>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="公司名稱">
                {{ aiStore.analysisResult.customer_info.company_name || '未提及' }}
              </el-descriptions-item>
              <el-descriptions-item label="業務類型">
                {{ aiStore.analysisResult.customer_info.business_type || '未知' }}
              </el-descriptions-item>
              <el-descriptions-item label="物件數量">
                <el-tag v-if="aiStore.analysisResult.customer_info.property_count" type="success">
                  {{ aiStore.analysisResult.customer_info.property_count }} 間
                </el-tag>
                <span v-else>未提及</span>
              </el-descriptions-item>
              <el-descriptions-item label="人員數量">
                <el-tag v-if="aiStore.analysisResult.customer_info.staff_count" type="info">
                  {{ aiStore.analysisResult.customer_info.staff_count }} 人
                </el-tag>
                <span v-else>未提及</span>
              </el-descriptions-item>
            </el-descriptions>

            <!-- 痛點 -->
            <div v-if="aiStore.analysisResult.customer_info.pain_points?.length" class="pain-points">
              <el-divider content-position="left">主要痛點</el-divider>
              <el-tag
                v-for="(point, index) in aiStore.analysisResult.customer_info.pain_points"
                :key="index"
                type="warning"
                class="pain-point-tag"
              >
                {{ point }}
              </el-tag>
            </div>
          </el-card>

          <!-- AA 客戶評估 -->
          <el-card shadow="hover" class="aa-card" v-if="aiStore.aaAssessment">
            <template #header>
              <div class="aa-header">
                <span>⭐ AA 客戶評估</span>
                <el-tag :type="aiStore.aaAssessment.is_aa_customer ? 'success' : 'info'" size="large">
                  {{ aiStore.aaAssessment.is_aa_customer ? 'AA 客戶' : '非 AA 客戶' }}
                </el-tag>
              </div>
            </template>

            <div class="aa-content">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="score-item">
                    <div class="score-label">評分</div>
                    <el-progress
                      type="circle"
                      :percentage="aiStore.aaAssessment.score"
                      :color="getScoreColor(aiStore.aaAssessment.score)"
                    />
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="score-item">
                    <div class="score-label">信心度</div>
                    <el-progress
                      type="circle"
                      :percentage="aiStore.aaAssessment.confidence"
                      color="#409eff"
                    />
                  </div>
                </el-col>
              </el-row>

              <el-divider content-position="left">判定原因</el-divider>
              <ul class="reasons-list">
                <li v-for="(reason, index) in aiStore.aaAssessment.reasons" :key="index">
                  {{ reason }}
                </li>
              </ul>
            </div>
          </el-card>

          <!-- 匹配的問卷問題 -->
          <el-card shadow="hover" class="questions-card">
            <template #header>
              <div class="questions-header">
                <span>✅ 匹配的問卷問題</span>
                <el-tag type="success">{{ aiStore.analysisResult.matched_questions.length }} 題</el-tag>
              </div>
            </template>

            <el-timeline>
              <el-timeline-item
                v-for="(question, index) in aiStore.analysisResult.matched_questions"
                :key="index"
                :timestamp="`信心度: ${question.confidence}%`"
                placement="top"
                :type="getConfidenceType(question.confidence)"
              >
                <el-card>
                  <div class="question-item">
                    <div class="question-number">問題 {{ question.question_number }}</div>
                    <div class="question-text">{{ question.question_text }}</div>
                    <el-divider />
                    <div class="question-answer">
                      <strong>答案：</strong>{{ question.answer }}
                    </div>
                    <div class="question-evidence">
                      <el-tag size="small" type="info">證據</el-tag>
                      {{ question.evidence }}
                    </div>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </div>

        <!-- 空狀態 -->
        <el-card v-else shadow="hover">
          <el-empty description="請輸入對談記錄並開始分析">
            <el-icon :size="100" color="#909399"><ChatDotRound /></el-icon>
          </el-empty>
        </el-card>
      </el-col>
    </el-row>

    <!-- 儲存為拜訪記錄對話框 -->
    <el-dialog
      v-model="saveDialogVisible"
      title="儲存為拜訪記錄"
      width="500px"
    >
      <el-form :model="saveForm" label-width="100px">
        <el-form-item label="選擇客戶" required>
          <el-select
            v-model="saveForm.customer_id"
            placeholder="請選擇客戶"
            filterable
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

        <el-form-item label="拜訪類型" required>
          <el-radio-group v-model="saveForm.visit_type">
            <el-radio value="first_visit">一訪</el-radio>
            <el-radio value="second_visit">二訪</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="拜訪日期" required>
          <el-date-picker
            v-model="saveForm.visit_date"
            type="datetime"
            placeholder="選擇拜訪日期時間"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="拜訪狀態">
          <el-select v-model="saveForm.visit_status" style="width: 100%">
            <el-option label="已完成" value="completed" />
            <el-option label="已排程" value="scheduled" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="saveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveVisit" :loading="saving">
          確定儲存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { UploadFilled, ChatDotRound, DocumentAdd } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus'
import { useAIStore } from '@/stores/ai'
import { customerApi } from '@/api/customer'
import { visitApi } from '@/api/visit'

const aiStore = useAIStore()
const router = useRouter()

// 對談文字
const conversationText = ref('')

// 客戶列表
const customers = ref<any[]>([])

// 儲存對話框
const saveDialogVisible = ref(false)
const saving = ref(false)

// 儲存表單
const saveForm = ref({
  customer_id: '',
  visit_type: 'first_visit',
  visit_date: new Date(),
  visit_status: 'completed'
})

// 載入客戶列表
onMounted(async () => {
  try {
    const response = await customerApi.getCustomers()
    customers.value = response.data || []
  } catch (error) {
    console.error('載入客戶列表失敗:', error)
  }
})

// 範例對談
const examples = {
  1: `你
 你們現在管理幾間物件？
業者
 大概 250 間左右，而且還在快速增加中。
你
 哇，規模不小！都是包租還是代管？
業者
 大概 7 成包租，3 成代管。我們主要做包租，每個月都要開差額發票給屋主。
你
 那人力配置怎麼樣？
業者
 我們有完整的團隊，3 個業務、2 個會計、1 個客服主管，總共 8 個人。
你
 有外國房客嗎？
業者
 有啊，大概佔 2 成，主要是日本人和韓國人。我們還有英文客服。
你
 未來有什麼規劃嗎？
業者
 我們明年計劃在台中開分公司，預計再增加 150 間物件。`,

  2: `你
 你好，請問你們是做包租代管的嗎？
業者
 對，我是自己做的，剛起步。
你
 現在有幾間物件？
業者
 15 間，都是套房，在新北。
你
 一個人處理嗎？
業者
 對，目前就我自己。租客有問題都 LINE 我。
你
 那會不會很忙？
業者
 還好，就是收租的時候比較忙，要一個一個催。`
}

// 載入範例
function loadExample(exampleNum: 1 | 2) {
  conversationText.value = examples[exampleNum]
  ElMessage.success(`已載入範例 ${exampleNum}`)
}

// 開始分析
async function handleAnalyze() {
  if (!conversationText.value.trim()) {
    ElMessage.warning('請輸入對談記錄')
    return
  }

  await aiStore.analyzeConversation(conversationText.value)
}

// 文件上傳
function handleFileChange(file: UploadFile) {
  const reader = new FileReader()
  reader.onload = (e) => {
    conversationText.value = e.target?.result as string
    ElMessage.success('文件載入成功')
  }
  reader.readAsText(file.raw!)
}

// 清空
function handleClear() {
  conversationText.value = ''
  aiStore.reset()
}

// 信心度類型
function getConfidenceType(confidence: number): 'primary' | 'success' | 'warning' {
  if (confidence >= 90) return 'success'
  if (confidence >= 70) return 'primary'
  return 'warning'
}

// 評分顏色
function getScoreColor(score: number): string {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

// 顯示儲存對話框
function showSaveDialog() {
  saveDialogVisible.value = true
}

// 儲存為拜訪記錄
async function handleSaveVisit() {
  if (!saveForm.value.customer_id) {
    ElMessage.warning('請選擇客戶')
    return
  }

  saving.value = true
  try {
    // 準備拜訪記錄資料
    const visitData = {
      customer_id: saveForm.value.customer_id,
      visit_type: saveForm.value.visit_type,
      visit_date: saveForm.value.visit_date.toISOString(),
      visit_status: saveForm.value.visit_status,
      // 填入 AI 分析的問卷資料
      questionnaire_data: aiStore.getQuestionnaireData(),
      // 儲存對談逐字稿
      conversation_transcript: aiStore.currentConversationText,
      // 標記為 AI 分析
      ai_analyzed: true,
      // 儲存分析摘要到備註
      notes: aiStore.analysisResult?.summary || ''
    }

    // 呼叫 API 建立拜訪記錄
    await visitApi.create(visitData)

    ElMessage.success('已儲存為拜訪記錄')
    saveDialogVisible.value = false

    // 詢問是否跳轉到拜訪記錄頁面
    setTimeout(() => {
      ElMessage({
        type: 'info',
        message: '是否前往拜訪記錄頁面？',
        showClose: true,
        duration: 5000
      })
      router.push('/visits')
    }, 1000)
  } catch (error) {
    console.error('儲存拜訪記錄失敗:', error)
    ElMessage.error('儲存失敗，請稍後再試')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped lang="scss">
.ai-analysis-page {
  .page-header {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      font-size: 24px;
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .upload-demo {
    margin: 20px 0;
  }

  .example-buttons {
    display: flex;
    gap: 10px;
    margin-top: 15px;
    justify-content: center;
  }

  .loading-container {
    height: 100%;
  }

  .analysis-results {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .summary-card {
    .summary-text {
      line-height: 1.8;
      color: #606266;
      margin: 0;
    }
  }

  .info-card {
    .pain-points {
      margin-top: 15px;
    }

    .pain-point-tag {
      margin: 5px 5px 5px 0;
    }
  }

  .aa-card {
    .aa-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .aa-content {
      .score-item {
        text-align: center;

        .score-label {
          font-size: 14px;
          color: #606266;
          margin-bottom: 15px;
        }
      }

      .reasons-list {
        margin: 0;
        padding-left: 20px;

        li {
          margin: 8px 0;
          color: #606266;
          line-height: 1.6;
        }
      }
    }
  }

  .questions-card {
    .questions-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .question-item {
      .question-number {
        display: inline-block;
        background: #409eff;
        color: white;
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 12px;
        margin-bottom: 8px;
      }

      .question-text {
        font-size: 15px;
        font-weight: bold;
        color: #303133;
        margin-bottom: 10px;
      }

      .question-answer {
        margin: 10px 0;
        color: #409eff;
      }

      .question-evidence {
        margin-top: 10px;
        padding: 10px;
        background: #f5f7fa;
        border-radius: 4px;
        font-size: 13px;
        color: #606266;
        line-height: 1.6;
      }
    }
  }
}
</style>
