<template>
  <div class="audio-player">
    <audio
      ref="audioElement"
      :src="src"
      @loadedmetadata="onLoadedMetadata"
      @timeupdate="onTimeUpdate"
      @ended="onEnded"
      @error="onError"
    ></audio>

    <div class="player-controls">
      <!-- 播放/暫停按鈕 -->
      <el-button
        :icon="isPlaying ? VideoPause : VideoPlay"
        circle
        @click="togglePlay"
        :disabled="!src || hasError"
      />

      <!-- 當前時間 -->
      <span class="time-display">{{ formatTime(currentTime) }}</span>

      <!-- 進度條 -->
      <el-slider
        v-model="sliderValue"
        class="progress-slider"
        :disabled="!src || hasError"
        @change="onSliderChange"
        :show-tooltip="false"
      />

      <!-- 總時長 -->
      <span class="time-display">{{ formatTime(totalDuration) }}</span>

      <!-- 播放速度 -->
      <el-select
        v-model="playbackRate"
        class="speed-select"
        size="small"
        @change="onSpeedChange"
        :disabled="!src || hasError"
      >
        <el-option label="0.5x" :value="0.5" />
        <el-option label="1.0x" :value="1.0" />
        <el-option label="1.5x" :value="1.5" />
        <el-option label="2.0x" :value="2.0" />
      </el-select>

      <!-- 音量控制 -->
      <el-icon class="volume-icon" :size="18">
        <component :is="volumeIcon" />
      </el-icon>
      <el-slider
        v-model="volume"
        class="volume-slider"
        :min="0"
        :max="100"
        @change="onVolumeChange"
        :show-tooltip="false"
      />
    </div>

    <!-- 錯誤提示 -->
    <div v-if="hasError" class="error-message">
      <el-alert type="error" :closable="false">
        無法載入音訊檔案，請檢查檔案是否存在或格式是否正確
      </el-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { VideoPlay, VideoPause, Mute, MuteNotification } from '@element-plus/icons-vue'

// Props
interface Props {
  src?: string // 音訊 URL
  duration?: number // 可選的預設時長（秒）
}

const props = withDefaults(defineProps<Props>(), {
  src: '',
  duration: 0
})

// Refs
const audioElement = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const totalDuration = ref(props.duration || 0)
const sliderValue = ref(0)
const playbackRate = ref(1.0)
const volume = ref(100)
const hasError = ref(false)

// Computed
const volumeIcon = computed(() => {
  return volume.value === 0 ? Mute : MuteNotification
})

// Methods
const togglePlay = () => {
  if (!audioElement.value) return

  if (isPlaying.value) {
    audioElement.value.pause()
    isPlaying.value = false
  } else {
    audioElement.value.play()
    isPlaying.value = true
  }
}

const onLoadedMetadata = () => {
  if (audioElement.value) {
    totalDuration.value = audioElement.value.duration
    hasError.value = false
  }
}

const onTimeUpdate = () => {
  if (audioElement.value) {
    currentTime.value = audioElement.value.currentTime
    // 更新進度條（避免拖動時的衝突）
    if (!isDragging.value) {
      sliderValue.value = (currentTime.value / totalDuration.value) * 100
    }
  }
}

const onEnded = () => {
  isPlaying.value = false
  currentTime.value = 0
  sliderValue.value = 0
}

const onError = () => {
  hasError.value = true
  isPlaying.value = false
  console.error('Audio player error: Failed to load audio file')
}

const onSliderChange = (value: number) => {
  if (audioElement.value) {
    const newTime = (value / 100) * totalDuration.value
    audioElement.value.currentTime = newTime
    currentTime.value = newTime
  }
}

const onSpeedChange = (rate: number) => {
  if (audioElement.value) {
    audioElement.value.playbackRate = rate
  }
}

const onVolumeChange = (vol: number) => {
  if (audioElement.value) {
    audioElement.value.volume = vol / 100
  }
}

const formatTime = (seconds: number): string => {
  if (!seconds || isNaN(seconds)) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 防止拖動時的衝突
const isDragging = ref(false)

// Watch for src changes
watch(
  () => props.src,
  (newSrc) => {
    if (newSrc) {
      hasError.value = false
      isPlaying.value = false
      currentTime.value = 0
      sliderValue.value = 0
      if (audioElement.value) {
        audioElement.value.load()
      }
    }
  }
)

// Cleanup
onBeforeUnmount(() => {
  if (audioElement.value) {
    audioElement.value.pause()
  }
})
</script>

<style scoped>
.audio-player {
  width: 100%;
}

.player-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.time-display {
  font-size: 14px;
  color: #606266;
  min-width: 45px;
  text-align: center;
}

.progress-slider {
  flex: 1;
  margin: 0 8px;
}

.speed-select {
  width: 80px;
}

.volume-icon {
  color: #606266;
  margin-left: 8px;
}

.volume-slider {
  width: 100px;
}

.error-message {
  margin-top: 12px;
}

/* 隱藏原生 audio 元素 */
audio {
  display: none;
}
</style>
