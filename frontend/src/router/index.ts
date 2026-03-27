import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Dashboard/Index.vue'),
        meta: { title: '儀表板' },
      },
      {
        path: '/customers',
        name: 'Customers',
        component: () => import('@/views/Customers/Index.vue'),
        meta: { title: '客戶管理' },
      },
      {
        path: '/customers/:id',
        name: 'CustomerDetail',
        component: () => import('@/views/Customers/Detail.vue'),
        meta: { title: '客戶詳情' },
      },
      {
        path: '/visits',
        name: 'Visits',
        component: () => import('@/views/Visits/Index.vue'),
        meta: { title: '拜訪記錄' },
      },
      {
        path: '/visits/:id',
        name: 'VisitDetail',
        component: () => import('@/views/Visits/Detail.vue'),
        meta: { title: '拜訪詳情' },
      },
      {
        path: '/contracts',
        name: 'Contracts',
        component: () => import('@/views/Contracts/Index.vue'),
        meta: { title: '簽約管理' },
      },
      {
        path: '/leads/import',
        name: 'LeadsImport',
        component: () => import('@/views/Leads/Import.vue'),
        meta: { title: 'Excel 名單導入' },
      },
      {
        path: '/ai-analysis',
        name: 'AIAnalysis',
        component: () => import('@/views/AIAnalysis/Index.vue'),
        meta: { title: 'AI 對談分析' },
      },
      {
        path: '/reports',
        name: 'Reports',
        component: () => import('@/views/Reports/Index.vue'),
        meta: { title: '報表分析' },
      },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 導航守衛
router.beforeEach((to, from, next) => {
  // 設定頁面標題
  document.title = `${to.meta.title} - 業務行動成效評估系統` || '業務行動成效評估系統'
  next()
})

export default router
