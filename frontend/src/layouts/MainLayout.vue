<template>
  <el-container class="main-layout">
    <!-- 固定頂部導航欄 -->
    <el-header class="main-header">
      <div class="header-content">
        <div class="logo">
          <h1>JGB Smart Property</h1>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="header-menu"
          mode="horizontal"
          router
          @select="handleMenuSelect"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>儀表板</span>
          </el-menu-item>
          <el-menu-item index="/leads/import">
            <el-icon><Upload /></el-icon>
            <span>名單匯入</span>
          </el-menu-item>
          <el-menu-item index="/customers">
            <el-icon><User /></el-icon>
            <span>客戶管理</span>
          </el-menu-item>
          <el-menu-item index="/visits">
            <el-icon><Calendar /></el-icon>
            <span>拜訪記錄</span>
          </el-menu-item>
          <el-menu-item index="/contracts">
            <el-icon><Document /></el-icon>
            <span>簽約管理</span>
          </el-menu-item>
          <el-menu-item index="/ai-analysis">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI 分析</span>
          </el-menu-item>
          <el-menu-item index="/reports">
            <el-icon><DataAnalysis /></el-icon>
            <span>報表分析</span>
          </el-menu-item>
        </el-menu>
        <div class="header-actions">
          <el-badge :value="0" :hidden="true">
            <el-icon :size="20"><Bell /></el-icon>
          </el-badge>
        </div>
      </div>
    </el-header>

    <!-- 主要內容區域 -->
    <el-main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  HomeFilled,
  Upload,
  User,
  Calendar,
  Document,
  ChatDotRound,
  DataAnalysis,
  Bell
} from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = ref(route.path)

// 監聽路由變化，更新選中的菜單項
watch(
  () => route.path,
  (newPath) => {
    // 處理詳情頁面的情況（例如 /customers/123 應該高亮 /customers）
    if (newPath.startsWith('/customers/')) {
      activeMenu.value = '/customers'
    } else if (newPath.startsWith('/visits/')) {
      activeMenu.value = '/visits'
    } else {
      activeMenu.value = newPath
    }
  },
  { immediate: true }
)

function handleMenuSelect(index: string) {
  activeMenu.value = index
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
  width: 100%;
}

.main-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
  height: 60px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.header-content {
  display: flex;
  align-items: center;
  height: 100%;
  max-width: 1920px;
  margin: 0 auto;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  margin-right: 40px;
  min-width: 200px;
}

.logo h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
  line-height: 60px;
}

.header-menu {
  flex: 1;
  border-bottom: none;
}

.header-menu .el-menu-item {
  height: 60px;
  line-height: 60px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-left: 20px;
}

.header-actions .el-icon {
  cursor: pointer;
  color: #606266;
  transition: color 0.3s;
}

.header-actions .el-icon:hover {
  color: #409eff;
}

.main-content {
  margin-top: 60px;
  padding: 0;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
  overflow-y: auto;
}

/* 過場動畫 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 響應式設計 */
@media (max-width: 1200px) {
  .logo {
    min-width: 160px;
  }

  .logo h1 {
    font-size: 18px;
  }

  .header-menu .el-menu-item span {
    display: none;
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 10px;
  }

  .logo {
    min-width: auto;
    margin-right: 20px;
  }

  .logo h1 {
    font-size: 16px;
  }
}
</style>
