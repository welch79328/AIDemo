<template>
  <div class="file-upload-container">
    <el-upload
      ref="uploadRef"
      class="upload-area"
      :drag="drag"
      :action="''"
      :auto-upload="false"
      :accept="accept"
      :multiple="multiple"
      :limit="limit"
      :show-file-list="showFileList"
      :before-upload="handleBeforeUpload"
      :on-change="handleChange"
      :on-exceed="handleExceed"
      :on-remove="handleRemove"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖曳檔案到此處或 <em>點擊上傳</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          <slot name="tip">
            <span v-if="accept">僅支援 {{ acceptText }} 格式檔案</span>
            <span v-if="maxSize">，檔案大小不超過 {{ maxSizeText }}</span>
          </slot>
        </div>
      </template>
    </el-upload>

    <!-- 上傳進度 -->
    <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
      <el-progress :percentage="uploadProgress" :status="progressStatus" />
      <p class="progress-text">{{ progressText }}</p>
    </div>

    <!-- 檔案列表 -->
    <div v-if="fileList.length > 0 && showFileList" class="file-list">
      <div v-for="(file, index) in fileList" :key="index" class="file-item">
        <el-icon><document /></el-icon>
        <span class="file-name">{{ file.name }}</span>
        <span class="file-size">{{ formatFileSize(file.size) }}</span>
        <el-button
          type="danger"
          size="small"
          :icon="Delete"
          circle
          @click="removeFile(index)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Document, Delete } from '@element-plus/icons-vue'
import type { UploadFile, UploadInstance, UploadRawFile, UploadUserFile } from 'element-plus'

// Props
interface Props {
  accept?: string // 接受的檔案類型，例如 ".xlsx,.xls"
  maxSize?: number // 最大檔案大小（MB）
  multiple?: boolean // 是否支援多檔案上傳
  limit?: number // 最大檔案數量
  drag?: boolean // 是否啟用拖放
  showFileList?: boolean // 是否顯示檔案列表
}

const props = withDefaults(defineProps<Props>(), {
  accept: '',
  maxSize: 10,
  multiple: false,
  limit: 1,
  drag: true,
  showFileList: true
})

// Emits
interface Emits {
  (e: 'upload', files: File[]): void
  (e: 'error', message: string): void
  (e: 'change', files: File[]): void
  (e: 'remove', file: File, index: number): void
}

const emit = defineEmits<Emits>()

// State
const uploadRef = ref<UploadInstance>()
const fileList = ref<UploadUserFile[]>([])
const uploadProgress = ref(0)
const progressStatus = ref<'success' | 'exception' | 'warning' | ''>('')
const progressText = ref('')

// Computed
const acceptText = computed(() => {
  if (!props.accept) return '所有'
  return props.accept.replace(/\./g, '').replace(/,/g, ', ').toUpperCase()
})

const maxSizeText = computed(() => {
  if (props.maxSize < 1) {
    return `${props.maxSize * 1024} KB`
  }
  return `${props.maxSize} MB`
})

// Methods

/**
 * 格式化檔案大小
 */
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

/**
 * 驗證檔案大小
 */
function validateFileSize(file: File): boolean {
  const maxSizeBytes = props.maxSize * 1024 * 1024
  if (file.size > maxSizeBytes) {
    const errorMsg = `檔案 ${file.name} 大小超過限制 ${maxSizeText.value}`
    ElMessage.error(errorMsg)
    emit('error', errorMsg)
    return false
  }
  return true
}

/**
 * 驗證檔案類型
 */
function validateFileType(file: File): boolean {
  if (!props.accept) return true

  const acceptedTypes = props.accept.split(',').map(t => t.trim())
  const fileName = file.name.toLowerCase()
  const fileExt = fileName.substring(fileName.lastIndexOf('.'))

  const isAccepted = acceptedTypes.some(type => {
    if (type.startsWith('.')) {
      return fileName.endsWith(type.toLowerCase())
    }
    // MIME type
    return file.type === type
  })

  if (!isAccepted) {
    const errorMsg = `檔案 ${file.name} 類型不符，僅支援 ${acceptText.value} 格式`
    ElMessage.error(errorMsg)
    emit('error', errorMsg)
    return false
  }

  return true
}

/**
 * 上傳前驗證
 */
function handleBeforeUpload(rawFile: UploadRawFile): boolean {
  if (!validateFileType(rawFile)) {
    return false
  }

  if (!validateFileSize(rawFile)) {
    return false
  }

  return true
}

/**
 * 檔案變更處理
 */
function handleChange(uploadFile: UploadFile, uploadFiles: UploadFile[]) {
  fileList.value = uploadFiles

  // 提取 File 物件
  const files = uploadFiles
    .map(f => f.raw)
    .filter((f): f is File => f !== undefined)

  emit('change', files)
}

/**
 * 超過數量限制處理
 */
function handleExceed() {
  ElMessage.warning(`最多只能上傳 ${props.limit} 個檔案`)
}

/**
 * 移除檔案處理
 */
function handleRemove(uploadFile: UploadFile, uploadFiles: UploadFile[]) {
  const index = fileList.value.findIndex(f => f.uid === uploadFile.uid)
  if (index !== -1 && uploadFile.raw) {
    emit('remove', uploadFile.raw, index)
  }
  fileList.value = uploadFiles
}

/**
 * 手動移除檔案
 */
function removeFile(index: number) {
  if (uploadRef.value) {
    const file = fileList.value[index]
    if (file) {
      uploadRef.value.handleRemove(file)
    }
  }
}

/**
 * 觸發上傳
 */
function triggerUpload() {
  const files = fileList.value
    .map(f => f.raw)
    .filter((f): f is File => f !== undefined)

  if (files.length === 0) {
    ElMessage.warning('請先選擇檔案')
    return
  }

  emit('upload', files)
}

/**
 * 清空檔案列表
 */
function clearFiles() {
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  fileList.value = []
  uploadProgress.value = 0
  progressStatus.value = ''
  progressText.value = ''
}

/**
 * 更新上傳進度
 */
function updateProgress(percentage: number, text?: string) {
  uploadProgress.value = percentage

  if (percentage === 100) {
    progressStatus.value = 'success'
    progressText.value = text || '上傳完成'
  } else if (percentage < 0) {
    progressStatus.value = 'exception'
    progressText.value = text || '上傳失敗'
  } else {
    progressStatus.value = ''
    progressText.value = text || `上傳中... ${percentage}%`
  }
}

// Expose methods
defineExpose({
  triggerUpload,
  clearFiles,
  updateProgress,
  fileList
})
</script>

<style scoped>
.file-upload-container {
  width: 100%;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload) {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px;
}

.el-icon--upload {
  font-size: 67px;
  color: #8c939d;
  margin: 0 0 16px;
}

.el-upload__text {
  color: #606266;
  font-size: 14px;
}

.el-upload__text em {
  color: #409eff;
  font-style: normal;
}

.el-upload__tip {
  margin-top: 12px;
  color: #8c939d;
  font-size: 12px;
  line-height: 1.5;
}

.upload-progress {
  margin-top: 20px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.progress-text {
  margin-top: 8px;
  text-align: center;
  color: #606266;
  font-size: 14px;
}

.file-list {
  margin-top: 16px;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.file-item:hover {
  background-color: #e4e7ed;
}

.file-item .el-icon {
  margin-right: 8px;
  font-size: 20px;
  color: #409eff;
}

.file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #303133;
  font-size: 14px;
}

.file-size {
  margin-right: 12px;
  color: #8c939d;
  font-size: 12px;
}
</style>
