import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhTw from 'element-plus/dist/locale/zh-tw.mjs'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// 註冊 Pinia
app.use(createPinia())

// 註冊 Vue Router
app.use(router)

// 註冊 Element Plus
app.use(ElementPlus, {
  locale: zhTw,
})

// 註冊所有 Element Plus 圖標
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
