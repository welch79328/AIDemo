# AI 對談匯入使用指南

## 問題排查與解決

### 如果欄位沒有被填入，請檢查：

#### 1. 前端頁面是否正常載入
訪問：http://localhost:5173/visits
- 確認頁面能正常顯示
- 打開瀏覽器開發者工具（F12）查看是否有 JavaScript 錯誤

#### 2. 檢查前端容器狀態
```bash
docker-compose logs frontend --tail 20
```
如果看到編譯錯誤，執行：
```bash
docker-compose restart frontend
```

#### 3. 測試 AI 後端是否正常
```bash
curl -X POST "http://localhost:8001/api/v1/ai/analyze-conversation" \
  -H "Content-Type: application/json" \
  -d '{"conversation_text": "你\n你們現在大概幾間啊？\n業者\n一百多間"}'
```

## 使用步驟

### 1. 準備對談記錄

**推薦格式**：
```
你
你們現在大概管幾間啊？

業者
差不多80間左右吧。

你
那租客有問題都怎麼聯絡你們？

業者
LINE啊，我有開LINE OA。
```

**測試文件**：
- `test_scenarios/realistic_conversation.txt` - 完整正式對談（150間）
- `test_scenarios/casual_conversation.txt` - 口語化對談（80間）

### 2. 在拜訪記錄頁面匯入

1. 訪問 http://localhost:5173/visits
2. 點擊「新增拜訪記錄」
3. 填寫基本資訊（客戶、拜訪類型、日期）
4. 在問卷區域，點擊「匯入對談記錄」按鈕
5. 貼上對談文字或上傳 .txt 文件
6. 點擊「AI 分析並填入問卷」
7. 等待 5-10 秒
8. 檢查自動填入的答案

### 3. 檢查填入結果

AI 會根據對談內容智能填入以下欄位：

#### 自動填入的問題類型

**Q1 - 公司官網/FB**
- 識別關鍵字：FB、粉專、粉絲頁、https://
- 自動提取網址（如果有）
- 範例：「現在只有FB粉專」→ 官網 = 有

**Q2 - LINE 管理租客**
- 識別：LINE OA、LINE個人、LINE
- 範例：「有開LINE OA」→ LINE OA

**Q13 - 組織人力數據**
- 分別提取：總戶數、總人數、人員分工
- 範例：「80間，2個人」→ 總戶數=80，總人數=2

**Q19 - 會計部門**
- 識別：有/無
- 提取人數（支援中文數字：一、二、兩、三...）
- 範例：「有，兩個人」→ 有會計部門，人數=2

**Q20 - 作業方式/協力系統**
- 識別作業方式：紙本/系統
- **重要**：`q20_other_systems` 欄位需要**手動補充**具體使用的系統名稱
- AI 可能無法準確識別此問題，建議手動檢查並補充

**Q22 - 競品**
- 自動識別：飛豬、DDROOM、包管家
- 從對話中提取提到的競品名稱
- **注意**：只有明確提及的競品會被識別

**其他欄位**
- Q3: 公司名稱
- Q6: 物件比例
- Q8: 分布地點
- Q14: 帳務方式（含詳細說明）
- Q15: 大房東數量（含損益表勾選）
- Q16: 差額發票
- Q18: 外籍租客
- Q20: 作業方式（含協力系統）
- Q21: 官網需求
- Q22: 競品

## 常見問題

### Q: 為什麼有些欄位沒被填入？

**A: 可能的原因**

1. **對談中沒有提到該問題**
   - AI 只會填入對談中有明確提及的資訊
   - 解決：手動補充未提及的欄位

2. **AI 信心度不足**
   - 如果 AI 不確定答案，不會填入（避免錯誤）
   - 解決：檢查對談是否含糊不清，手動填入

3. **問題描述方式不同**
   - AI 使用關鍵字匹配
   - 解決：使用更明確的問題描述

### Q: 網址欄位沒有被填入？

**A: 可能原因**

1. 對談中沒有提供具體網址
   - 範例：「只有FB粉專」（沒有網址）
   - 解決：手動輸入網址

2. 網址格式不標準
   - 需要包含 `http://` 或 `https://`
   - 解決：手動輸入完整網址

### Q: 人數欄位沒有被填入？

**A: 檢查**

1. 對談中是否有明確的數字
   - ✓ 支援：「2人」、「兩個人」、「2位」
   - ✗ 不支援：「幾個人」、「一些人」

2. 現在已支援中文數字
   - 一、二、三、四、五、六、七、八、九、十、兩
   - 範例：「兩個人」→ 2

## 測試範例

### 測試 1：使用內建範例
```bash
# 複製測試文件
cat test_scenarios/casual_conversation.txt

# 在網頁中：
# 1. 新增拜訪記錄
# 2. 點擊「匯入對談記錄」
# 3. 貼上上述內容
# 4. 點擊「AI 分析並填入問卷」
```

### 測試 2：直接測試 API
```bash
python3 << 'EOF'
import requests

with open('test_scenarios/casual_conversation.txt', 'r', encoding='utf-8') as f:
    conversation = f.read()

response = requests.post(
    'http://localhost:8001/api/v1/ai/analyze-conversation',
    json={'conversation_text': conversation},
    timeout=30
)

result = response.json()
print(f"匹配到 {len(result['matched_questions'])} 個問題")
for q in result['matched_questions']:
    print(f"  - 問題 {q['question_number']}: {q['question_text'][:30]}...")
EOF
```

## 技術細節

### AI 映射邏輯

前端使用問題文本的關鍵字來判斷應該填入哪個欄位：

```javascript
// 範例：會計部門
if (questionText.includes('會計部門')) {
  // 判斷有/無
  if (answer.includes('有') || answer.includes('是')) {
    questionnaireForm.q19_has_accounting = 'Y'

    // 提取人數（阿拉伯數字或中文數字）
    const staffMatch = answer.match(/(\d+)\s*(?:人|位)/)
    if (staffMatch) {
      questionnaireForm.q19_accounting_staff = staffMatch[1]
    } else {
      const chineseMatch = answer.match(/(一|二|兩|三|...)\s*(?:人|位)/)
      // 轉換中文數字為阿拉伯數字
    }
  }
}
```

### 支援的資料類型

1. **單選** - Radio
   - 範例：是/否、紙本/系統/外包

2. **多選** - Checkbox
   - 範例：競品選擇、案場類型

3. **文字輸入** - Input
   - 範例：公司名稱、網址

4. **數字輸入** - Input (number)
   - 範例：總戶數、總人數

5. **文字區域** - Textarea
   - 範例：痛點描述、人員分工

6. **勾選框** - Checkbox (boolean)
   - 範例：需要做損益表

## 改進建議

### 提高 AI 準確度

1. **使用明確的問題**
   ```
   ✓ 好：「你們有幾間物件？」「80間」
   ✗ 差：「規模如何？」「還可以」
   ```

2. **包含具體數字**
   ```
   ✓ 好：「2個人」、「兩個會計」
   ✗ 差：「幾個人」、「一些員工」
   ```

3. **使用完整句子**
   ```
   ✓ 好：「我們有用LINE OA管理租客」
   ✗ 差：「LINE」
   ```

### 對談記錄最佳實踐

1. 保留原始對話格式
2. 標示清楚對話雙方（你/業者）
3. 包含 10 輪以上問答
4. 涵蓋關鍵問題（物件數、人員數、痛點等）

## 更新日誌

### 2026-03-20
- ✅ 支援中文數字提取（一、二、兩...）
- ✅ 改進官網/FB 識別（識別「粉專」關鍵字）
- ✅ 改進帳務方式、大房東等複合欄位
- ✅ 支援所有 22 題問卷（不限一訪/二訪）
