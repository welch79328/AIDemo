<template>
  <div class="interaction-timeline">
    <!-- 類型篩選 -->
    <div class="filter-bar">
      <el-radio-group v-model="selectedFilter" size="small" @change="onFilterChange">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button :label="InteractionType.DOCUMENT">文檔</el-radio-button>
        <el-radio-button :label="InteractionType.AUDIO">音訊</el-radio-button>
        <el-radio-button :label="InteractionType.STATUS_CHANGE">狀態變更</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 載入中狀態 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- 空狀態 -->
    <el-empty v-else-if="!loading && interactions.length === 0" description="暫無互動記錄" />

    <!-- 時間軸 -->
    <el-timeline v-else class="timeline-content">
      <el-timeline-item
        v-for="interaction in interactions"
        :key="interaction.id"
        :timestamp="formatTimestamp(interaction.created_at)"
        placement="top"
        :icon="getIcon(interaction.interaction_type)"
        :color="getColor(interaction.interaction_type)"
      >
        <!-- 標題 -->
        <div class="timeline-item-header">
          <span class="item-type-tag">
            <el-tag :type="getTagType(interaction.interaction_type)" size="small">
              {{ getTypeName(interaction.interaction_type) }}
            </el-tag>
          </span>
          <span class="item-title">{{ interaction.title || '無標題' }}</span>
        </div>

        <!-- 內容區 -->
        <div class="timeline-item-content">
          <!-- 文檔類型 -->
          <template v-if="interaction.interaction_type === InteractionType.DOCUMENT">
            <div class="document-info">
              <el-icon class="file-icon"><Document /></el-icon>
              <div class="file-details">
                <div class="file-name">{{ interaction.file_name }}</div>
                <div class="file-meta">
                  大小: {{ formatFileSize(interaction.file_size) }}
                  <span v-if="interaction.file_type"> | 類型: {{ interaction.file_type }}</span>
                </div>
              </div>
              <el-button
                type="primary"
                size="small"
                :icon="Download"
                @click="downloadFile(interaction)"
              >
                下載
              </el-button>
            </div>
          </template>

          <!-- 音訊類型 -->
          <template v-else-if="interaction.interaction_type === InteractionType.AUDIO">
            <div class="audio-info">
              <div class="audio-meta">
                <el-icon class="file-icon"><Microphone /></el-icon>
                <div class="file-details">
                  <div class="file-name">{{ interaction.file_name }}</div>
                  <div class="file-meta">
                    時長: {{ formatDuration(interaction.audio_duration) }}
                    <span v-if="interaction.file_size">
                      | 大小: {{ formatFileSize(interaction.file_size) }}
                    </span>
                  </div>
                </div>
              </div>
              <!-- AudioPlayer 播放器 -->
              <AudioPlayer
                v-if="interaction.file_path"
                :src="getFileUrl(interaction.file_path)"
                :duration="interaction.audio_duration"
              />
              <!-- 文字稿 -->
              <div v-if="interaction.transcript_text" class="transcript">
                <el-divider content-position="left">文字稿</el-divider>
                <div class="transcript-text">{{ interaction.transcript_text }}</div>
              </div>
            </div>
          </template>

          <!-- 狀態變更類型 -->
          <template v-else-if="interaction.interaction_type === InteractionType.STATUS_CHANGE">
            <div class="status-change-info">
              <el-icon class="status-icon"><Edit /></el-icon>
              <div class="status-content">
                {{ interaction.notes || '狀態已變更' }}
              </div>
            </div>
          </template>

          <!-- 備註 -->
          <div v-if="interaction.notes && interaction.interaction_type !== InteractionType.STATUS_CHANGE" class="notes">
            <el-divider content-position="left">備註</el-divider>
            <div class="notes-text">{{ interaction.notes }}</div>
          </div>
        </div>
      </el-timeline-item>
    </el-timeline>

    <!-- 分頁 -->
    <div v-if="!loading && total > limit" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="limit"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next"
        @current-change="loadInteractions"
        @size-change="loadInteractions"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document,
  Microphone,
  Edit,
  Download
} from '@element-plus/icons-vue'
import AudioPlayer from './AudioPlayer.vue'
import {
  getInteractions,
  type Interaction,
  type InteractionQueryParams,
  InteractionType
} from '@/api/interaction'

// Props
interface Props {
  customerId: string
  filter?: InteractionType | ''
}

const props = withDefaults(defineProps<Props>(), {
  filter: ''
})

// Emits
const emit = defineEmits<{
  loaded: [interactions: Interaction[]]
}>()

// State
const interactions = ref<Interaction[]>([])
const loading = ref(false)
const currentPage = ref(1)
const limit = ref(20)
const total = ref(0)
const selectedFilter = ref<InteractionType | ''>(props.filter)

// Methods
const loadInteractions = async () => {
  loading.value = true
  try {
    const params: InteractionQueryParams = {
      customer_id: props.customerId,
      page: currentPage.value,
      limit: limit.value
    }

    if (selectedFilter.value) {
      params.interaction_type = selectedFilter.value
    }

    const response = await getInteractions(params)
    interactions.value = response.interactions
    total.value = response.total

    emit('loaded', response.interactions)
  } catch (error) {
    console.error('Failed to load interactions:', error)
    ElMessage.error('載入互動記錄失敗')
  } finally {
    loading.value = false
  }
}

const onFilterChange = () => {
  currentPage.value = 1
  loadInteractions()
}

const getIcon = (type: string) => {
  switch (type) {
    case InteractionType.DOCUMENT:
      return Document
    case InteractionType.AUDIO:
      return Microphone
    case InteractionType.STATUS_CHANGE:
      return Edit
    default:
      return Document
  }
}

const getColor = (type: string) => {
  switch (type) {
    case InteractionType.DOCUMENT:
      return '#409EFF'
    case InteractionType.AUDIO:
      return '#67C23A'
    case InteractionType.STATUS_CHANGE:
      return '#E6A23C'
    default:
      return '#909399'
  }
}

const getTagType = (type: string): 'primary' | 'success' | 'warning' => {
  switch (type) {
    case InteractionType.DOCUMENT:
      return 'primary'
    case InteractionType.AUDIO:
      return 'success'
    case InteractionType.STATUS_CHANGE:
      return 'warning'
    default:
      return 'primary'
  }
}

const getTypeName = (type: string) => {
  switch (type) {
    case InteractionType.DOCUMENT:
      return '文檔'
    case InteractionType.AUDIO:
      return '音訊'
    case InteractionType.STATUS_CHANGE:
      return '狀態變更'
    default:
      return '未知'
  }
}

const formatTimestamp = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return minutes === 0 ? '剛剛' : `${minutes} 分鐘前`
    }
    return `${hours} 小時前`
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days} 天前`
  }

  return date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatFileSize = (bytes?: number) => {
  if (!bytes) return 'N/A'
  const kb = bytes / 1024
  const mb = kb / 1024
  return mb >= 1 ? `${mb.toFixed(2)} MB` : `${kb.toFixed(2)} KB`
}

const formatDuration = (seconds?: number) => {
  if (!seconds) return 'N/A'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const getFileUrl = (filePath: string) => {
  // 建構檔案完整 URL（假設後端提供靜態檔案服務）
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'
  return `${baseUrl}/storage/${filePath}`
}

const downloadFile = (interaction: Interaction) => {
  if (interaction.file_path) {
    const fileUrl = getFileUrl(interaction.file_path)
    const link = document.createElement('a')
    link.href = fileUrl
    link.download = interaction.file_name || 'download'
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

// 暴露方法供父元件呼叫
const refresh = () => {
  loadInteractions()
}

defineExpose({
  refresh
})

// Lifecycle
onMounted(() => {
  loadInteractions()
})
</script>

<style scoped>
.interaction-timeline {
  width: 100%;
}

.filter-bar {
  margin-bottom: 20px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.loading-container {
  padding: 20px;
}

.timeline-content {
  padding: 12px 0;
}

.timeline-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.item-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.timeline-item-content {
  background-color: #f9fafb;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.document-info,
.audio-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  font-size: 32px;
  color: #409EFF;
}

.file-details {
  flex: 1;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.file-meta {
  font-size: 12px;
  color: #909399;
}

.audio-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.transcript {
  margin-top: 12px;
}

.transcript-text {
  padding: 12px;
  background-color: #fff;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.status-change-info {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.status-icon {
  font-size: 24px;
  color: #E6A23C;
  margin-top: 2px;
}

.status-content {
  flex: 1;
  line-height: 1.6;
}

.notes {
  margin-top: 12px;
}

.notes-text {
  padding: 12px;
  background-color: #fff;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  line-height: 1.6;
  color: #606266;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>
