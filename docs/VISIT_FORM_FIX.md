# 拜訪記錄表單修復說明

## 問題描述

使用者回報：「建立拜訪記錄失敗」

## 根本原因

1. **日期格式問題**：Element Plus 的日期選擇器 `value-format` 設定為 `"YYYY-MM-DDTHH:mm:ss[Z]"` 中的 `[Z]` 語法未被正確處理
2. **錯誤訊息不明確**：當表單驗證失敗時，只顯示通用錯誤訊息「建立拜訪記錄失敗」，沒有顯示具體的驗證錯誤

## 解決方案

### 1. 修復日期格式 (frontend/src/views/Visits/Index.vue)

**修改前**：
```vue
<el-date-picker
  v-model="formData.visit_date"
  type="datetime"
  placeholder="選擇日期時間"
  format="YYYY-MM-DD HH:mm"
  value-format="YYYY-MM-DDTHH:mm:ss[Z]"
/>
```

**修改後**：
```vue
<el-date-picker
  v-model="formData.visit_date"
  type="datetime"
  placeholder="選擇日期時間"
  format="YYYY-MM-DD HH:mm"
  value-format="YYYY-MM-DDTHH:mm:ss"
/>
```

**變更說明**：
- 移除 `[Z]` 後綴，改用 `YYYY-MM-DDTHH:mm:ss` 格式
- 這會產生類似 `2026-03-20T15:30:00` 的 ISO 格式日期字串
- 後端 Pydantic 可以正確解析此格式

### 2. 改善錯誤訊息 (frontend/src/stores/visit.ts)

**修改前**：
```typescript
catch (error) {
  console.error('建立拜訪記錄失敗:', error)
  ElMessage.error('建立拜訪記錄失敗')
  throw error
}
```

**修改後**：
```typescript
catch (error: any) {
  console.error('建立拜訪記錄失敗:', error)
  // 顯示詳細的驗證錯誤
  if (error?.response?.data?.detail) {
    const details = error.response.data.detail
    if (Array.isArray(details)) {
      const errorMsg = details.map((d: any) => {
        const field = d.loc.join(' > ')
        return `${field}: ${d.msg}`
      }).join('\n')
      ElMessage.error({
        message: `建立拜訪記錄失敗：\n${errorMsg}`,
        duration: 5000
      })
    } else {
      ElMessage.error(`建立拜訪記錄失敗：${details}`)
    }
  } else {
    ElMessage.error('建立拜訪記錄失敗')
  }
  throw error
}
```

**變更說明**：
- 解析後端返回的 Pydantic 驗證錯誤
- 顯示具體的欄位和錯誤訊息
- 例如：`body > visit_date: Input should be a valid datetime, input is too short`

## 驗證步驟

### 測試 1：正常建立拜訪記錄
1. 訪問 http://localhost:5173/visits
2. 點擊「新增拜訪記錄」
3. 選擇客戶、拜訪類型、**拜訪日期**、拜訪狀態
4. 點擊「確定」
5. ✅ 應該成功建立拜訪記錄

### 測試 2：驗證錯誤訊息
1. 訪問 http://localhost:5173/visits
2. 點擊「新增拜訪記錄」
3. 選擇客戶、拜訪類型，**不選擇拜訪日期**
4. 點擊「確定」
5. ✅ 應該顯示表單驗證錯誤：「請選擇拜訪日期」

### 測試 3：後端 API 驗證
```bash
# 測試空日期（應該失敗）
curl -X POST "http://localhost:8001/api/v1/visits" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "test-id",
    "visit_type": "first_visit",
    "visit_date": "",
    "visit_status": "scheduled"
  }'

# 預期回應：422 Unprocessable Entity
# {"detail":[{"type":"datetime_parsing","loc":["body","visit_date"],"msg":"Input should be a valid datetime, input is too short",...}]}
```

```bash
# 測試正確格式（應該成功）
curl -X POST "http://localhost:8001/api/v1/visits" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "actual-customer-uuid",
    "visit_type": "first_visit",
    "visit_date": "2026-03-20T15:30:00",
    "visit_status": "scheduled"
  }'

# 預期回應：201 Created（前提是 customer_id 存在）
```

## 修改檔案

- `frontend/src/views/Visits/Index.vue` (行 189, 435)
- `frontend/src/stores/visit.ts` (行 83-103)

## 部署狀態

✅ 已套用（透過 HMR 熱更新）

使用者現在可以：
1. 正常建立拜訪記錄（當所有必填欄位都填寫時）
2. 看到清楚的驗證錯誤訊息（當必填欄位缺少時）
