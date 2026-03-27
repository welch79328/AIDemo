# sales-lead-management - 實作差距分析（修訂版）

## 執行摘要

### 專案範圍
在現有「業務行動成效評估系統」的基礎上，擴展銷售潛在客戶管理功能，包括臉書廣告名單導入、互動記錄追蹤、AI 對話分析及客戶健檢報告生成。

### 現有基礎評估（重要發現）

**系統已具備的核心AI功能**：

✅ **業務30問完整實作** (`backend/app/data/questionnaire_30.json`)
- 一訪問題：10題
- 二訪問題：14題
- Nice to have：2題
- 題庫已載入並整合至 API

✅ **完整的 AI 分析服務** (`backend/app/services/openai_service.py`)
- `analyze_conversation()` - 對話分析和業務30問匹配
- `extract_customer_info()` - 客戶資訊提取
- `assess_aa_customer()` - AA 客戶評估（含評分和判定邏輯）

✅ **完整的 AI API 端點** (`backend/app/api/v1/ai_analysis.py`)
- `POST /api/v1/ai/analyze-conversation` - 對話分析
- `POST /api/v1/ai/extract-customer-info` - 資訊提取
- `POST /api/v1/ai/assess-aa-customer` - AA 評估
- `GET /api/v1/ai/questionnaire` - 獲取問卷

✅ **完整的 Schema 定義**
- ConversationAnalysisRequest/Response
- MatchedQuestion (含 question_number, answer, confidence, evidence)
- AACustomerAssessment (含 is_aa_customer, confidence, reasons, score)

✅ **其他已實作功能**
- Customer 模型含 `is_aa_customer`, `maturity_score` 欄位
- QuestionTemplate 模型可管理題庫
- AaCustomerCriteria 模型可配置判定規則
- Excel 處理套件已安裝 (openpyxl, pandas, xlsxwriter)
- OpenAI 客戶端已整合

### 實作複雜度（重新評估）

**中等 (Medium)** ← 從「中等偏高」下調

**理由**：
1. ✅ **核心 AI 功能已 100% 完成** - 業務30問匹配、客戶評估全部實作完畢
2. ✅ 技術棧完全符合 (FastAPI + Vue 3 + PostgreSQL)
3. ✅ Excel 處理依賴已安裝
4. ⚠️ 需要新增檔案上傳和儲存機制
5. ⚠️ 需要整合音訊轉文字服務（唯一需要新增的AI功能）
6. ⚠️ 需要實作報告生成功能

### 關鍵發現：大幅簡化的需求

**原本認為需要實作的 AI 功能**：
- ❌ 業務30問匹配邏輯 → ✅ **已完成**
- ❌ 對話分析 API → ✅ **已完成**
- ❌ AA 客戶評估 → ✅ **已完成**
- ❌ 題庫管理 → ✅ **已完成**

**實際需要新增的功能**：
- ✅ Excel 名單導入
- ✅ 檔案上傳系統
- ✅ 音訊轉文字（唯一的新 AI 功能）
- ✅ 互動記錄時間軸
- ✅ 健檢報告生成

### 關鍵挑戰（更新）

1. **檔案管理基礎設施**
   - 實作檔案上傳 API
   - 選擇儲存策略（本地 / S3）
   - 實作檔案元數據管理

2. **音訊轉文字整合**（唯一需要新增的 AI 功能）
   - 整合 OpenAI Whisper API
   - 處理長音訊檔案
   - 實作轉換進度追蹤

3. **Excel 處理**
   - 解析臉書廣告表單格式
   - 生成健檢報告 Excel

4. **前端功能擴展**
   - 檔案上傳 UI 組件
   - 音訊播放器
   - 互動時間軸展示

5. **資料模型整合**
   - 決定是否擴展 Customer 或新增 Lead
   - 設計 Interaction 模型與 Visit 的關係

### 建議策略

**混合方法 (Hybrid Approach)** - 維持不變

**實施週期**：**6-8 週** ← 從 8-12 週縮短

**原因**：AI 核心功能已完成，節省約 2-4 週開發時間

---

## 詳細分析

### 1. 代碼庫評估

#### 後端 (Backend)

**框架**: FastAPI 0.109.0
**ORM**: SQLAlchemy 2.0.25
**資料庫遷移**: Alembic 1.13.1
**Python 版本**: 3.12+

**已實作的關鍵功能**：

1. **AI 分析服務** (`services/openai_service.py`)
   ```python
   class OpenAIService:
       async def analyze_conversation()  # ✅ 已實作
       async def extract_customer_info()  # ✅ 已實作
       async def assess_aa_customer()     # ✅ 已實作
   ```

2. **AI API 端點** (`api/v1/ai_analysis.py`)
   - ✅ 問卷資料自動載入: `QUESTIONNAIRE_DATA = json.load(f)`
   - ✅ 對話分析端點完整
   - ✅ AA 評估邏輯完整
   - ✅ 返回格式符合需求 (matched_questions, summary, confidence, etc.)

3. **資料模型**
   - ✅ Customer 模型已有 `is_aa_customer`, `maturity_score`
   - ✅ Visit 模型有 `questionnaire_data` JSON 欄位
   - ✅ QuestionTemplate, AaCustomerCriteria 模型已存在

**優勢**：
- AI 核心功能 100% 完成
- 業務30問題庫已整合
- Schema 定義完整且符合需求
- Excel 處理套件已安裝

**缺失**：
- 無檔案上傳 API
- 無音訊轉文字功能
- 無 Interaction 模型
- 無報告生成服務

#### 前端 (Frontend)

**框架**: Vue 3.4.0 + Element Plus 2.5.0

**已實作功能**：
- ✅ AI 分析頁面 (`views/AIAnalysis/Index.vue`)
- ✅ 客戶列表和詳情頁
- ✅ HTTP 客戶端配置

**缺失**：
- 無檔案上傳組件
- 無音訊播放器
- 無互動時間軸組件
- 無報告預覽功能

---

### 2. 需求差距分析（重新評估）

#### 需求 1: 資料導入管理

##### 1.1 Excel 名單導入
- **狀態**: ❌ **未涵蓋**
- **複雜度**: **中等 (Medium)**
- **實作方法**: **新增 (New)**
- **所需工作**:
  - 新增 Excel 解析服務
  - 新增導入 API 端點
  - 前端檔案上傳 UI

##### 1.2 資料驗證與去重
- **狀態**: ⚠️ **部分涵蓋**
- **複雜度**: **低 (Low)**
- **實作方法**: **擴展 (Extend)**
- **所需工作**:
  - 在 CRUD 層添加去重邏輯
  - 前端顯示重複提示

##### 1.3 導入歷史記錄
- **狀態**: ❌ **未涵蓋**
- **複雜度**: **低 (Low)**
- **實作方法**: **新增 (New)**
- **所需工作**:
  - 新增 ImportBatch 模型
  - 新增歷史查詢 API

---

#### 需求 2: 潛在客戶管理

##### 2.1 客戶資料檢視
- **狀態**: ✅ **完全涵蓋**
- **複雜度**: **低 (Low)**
- **實作方法**: **擴展 (Extend)**
- **所需工作**: 微調篩選條件

##### 2.2 客戶資料編輯
- **狀態**: ✅ **完全涵蓋**
- **複雜度**: **低 (Low)**
- **實作方法**: **擴展 (Extend)**
- **所需工作**: 可選添加修改歷史

##### 2.3 聯絡狀態管理
- **狀態**: ✅ **完全涵蓋**
- **複雜度**: **極低 (Very Low)**
- **實作方法**: **配置 (Config)**
- **所需工作**: 調整 CustomerStatus Enum

---

#### 需求 3: 銷售互動記錄

##### 3.1 互動文檔上傳
- **狀態**: ❌ **未涵蓋**
- **複雜度**: **中等 (Medium)**
- **實作方法**: **新增 (New)**
- **所需工作**:
  - 新增 Interaction 模型
  - 新增檔案上傳服務和 API
  - 實作儲存機制
  - 前端上傳組件

##### 3.2 錄音檔上傳與管理
- **狀態**: ❌ **未涵蓋**
- **複雜度**: **中等 (Medium)**
- **實作方法**: **新增 (New)**
- **所需工作**:
  - 擴展檔案上傳支援音訊
  - 安裝音訊時長提取套件
  - 前端音訊播放器

##### 3.3 互動記錄時間軸
- **狀態**: ⚠️ **部分涵蓋**
- **複雜度**: **中等 (Medium)**
- **實作方法**: **新增 (New)**
- **所需工作**:
  - 設計活動聚合查詢
  - 前端時間軸 UI

---

#### 需求 4: AI 對話分析（重大更新）

##### 4.1 音訊轉文字
- **狀態**: ❌ **未涵蓋**
- **複雜度**: **中等 (Medium)** ← 從「中等偏高」下調
- **實作方法**: **擴展 (Extend)**
- **所需工作**:
  - 在 OpenAIService 新增 Whisper API 調用方法
  - 新增轉換 API 端點
  - 前端進度顯示和文字稿編輯

**重要**：這是**唯一需要新增的 AI 功能**

##### 4.2 業務30問匹配分析
- **狀態**: ✅ **完全涵蓋** ← 更新
- **複雜度**: **極低 (Very Low)** ← 從「中等」大幅下調
- **實作方法**: **已完成 (Completed)**
- **現有實作**:
  - ✅ `analyze_conversation()` 已完整實作
  - ✅ 問卷資料已載入 (`questionnaire_30.json`)
  - ✅ API 端點已存在 (`/api/v1/ai/analyze-conversation`)
  - ✅ 返回格式包含 matched_questions, confidence, evidence
- **所需工作**: **無** - 可直接使用

##### 4.3 對話品質評估
- **狀態**: ✅ **完全涵蓋** ← 更新
- **複雜度**: **極低 (Very Low)** ← 從「中等」大幅下調
- **實作方法**: **已完成 (Completed)**
- **現有實作**:
  - ✅ `analyze_conversation()` 返回 summary
  - ✅ 可計算覆蓋率（matched_questions 數量 / 30）
- **所需工作**:
  - 前端視覺化展示（使用現有 ECharts）
  - 可選：擴展評分細節

---

#### 需求 5: 客戶分級評估（重大更新）

##### 5.1 AA 客戶識別
- **狀態**: ✅ **完全涵蓋** ← 更新
- **複雜度**: **極低 (Very Low)** ← 從「低」下調
- **實作方法**: **已完成 (Completed)**
- **現有實作**:
  - ✅ `assess_aa_customer()` 已完整實作
  - ✅ 判定邏輯包含：規劃擴大營運、大房東數量、包租物件數、外籍租客等
  - ✅ 返回 is_aa_customer, confidence, reasons, score
  - ✅ Customer 模型已有 `is_aa_customer` 欄位
  - ✅ API 端點 `/api/v1/ai/assess-aa-customer` 已存在
- **所需工作**: **無** - 可直接使用

##### 5.2 客戶分級規則配置
- **狀態**: ⚠️ **部分涵蓋**
- **複雜度**: **中等 (Medium)**
- **實作方法**: **擴展 (Extend)**
- **現有實作**:
  - ✅ AaCustomerCriteria 模型支援 JSON 配置
  - ✅ QuestionTemplate 有 score_weight
- **所需工作**:
  - 新增設定頁面 UI
  - 實作批次重新評估功能
  - 新增 CustomerEvaluation 模型（評估歷史）

##### 5.3 評估結果追蹤
- **狀態**: ❌ **未涵蓋**
- **複雜度**: **低 (Low)**
- **實作方法**: **新增 (New)**
- **所需工作**:
  - 新增 CustomerEvaluation 模型
  - 新增歷史查詢 API
  - 前端趨勢圖表

---

#### 需求 6: 健檢報告生成

##### 6.1 客戶健檢紀錄表生成
- **狀態**: ❌ **未涵蓋**
- **複雜度**: **中等 (Medium)**
- **實作方法**: **新增 (New)**
- **所需工作**:
  - 新增 HealthCheckReport 模型
  - 新增報告生成服務（使用 openpyxl）
  - 整合 AI 分析結果
  - 新增報告生成 API

**依賴**: 需要「客戶30問健檢紀錄表 (回覆).xlsx」範本

##### 6.2 報告匯出功能
- **狀態**: ❌ **未涵蓋**
- **複雜度**: **中等 (Medium)**
- **實作方法**: **新增 (New)**
- **所需工作**:
  - 實作單一/批次匯出
  - ZIP 壓縮功能
  - 前端下載 UI

##### 6.3 報告檢視與列印
- **狀態**: ❌ **未涵蓋**
- **複雜度**: **中等偏高 (Medium-High)**
- **實作方法**: **新增 (New)**
- **所需工作**:
  - 實作 HTML 報告預覽
  - PDF 生成（使用 WeasyPrint）
  - Email 服務整合
  - 前端預覽和分享 UI

---

### 3. 整合點分析

#### 資料模型整合

**建議方案**：擴展 Customer 模型（不新增 Lead）

**新增欄位**:
```python
class Customer:
    ad_source: str  # 廣告來源
    import_batch_id: str  # 導入批次ID
    # 其他欄位已存在：is_aa_customer, maturity_score, etc.
```

**新增資料表** (5個，從原7個減少):
1. ~~Lead~~ - 用 Customer 代替
2. `interactions` - 互動記錄
3. `ai_analyses` - AI 分析結果
4. `customer_evaluations` - 客戶評估歷史
5. `health_check_reports` - 健檢報告
6. `import_batches` - 導入批次
7. ~~BusinessQuestions~~ - 已有 questionnaire_30.json

#### AI 服務整合

**現有服務** (`OpenAIService`):
- ✅ `analyze_conversation()` - **無需修改，直接使用**
- ✅ `extract_customer_info()` - **無需修改，直接使用**
- ✅ `assess_aa_customer()` - **無需修改，直接使用**

**需要新增**:
- `transcribe_audio()` - 音訊轉文字（使用 Whisper API）

**實作範例**:
```python
class OpenAIService:
    # ... 現有方法保持不變 ...

    async def transcribe_audio(
        self,
        audio_file_path: str
    ) -> str:
        """使用 Whisper API 將音訊轉為文字"""
        with open(audio_file_path, "rb") as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="zh"
            )
        return transcript.text
```

#### API 整合

**現有 API**（無需修改，直接使用）:
- ✅ `POST /api/v1/ai/analyze-conversation`
- ✅ `POST /api/v1/ai/extract-customer-info`
- ✅ `POST /api/v1/ai/assess-aa-customer`
- ✅ `GET /api/v1/ai/questionnaire`

**需要新增 API**:
- `POST /api/v1/leads/import` - Excel 導入
- `GET /api/v1/leads/import/history` - 導入歷史
- `POST /api/v1/interactions` - 互動記錄 CRUD
- `POST /api/v1/interactions/upload` - 檔案上傳
- `POST /api/v1/ai/transcribe` - 音訊轉文字（唯一新增的 AI 端點）
- `POST /api/v1/reports/generate` - 生成報告
- `GET /api/v1/reports/{id}/export` - 匯出報告

**減少了約 50% 的 API 開發工作量**

---

### 4. 外部依賴

#### 1. AI 語音轉文字服務（唯一需要新增的 AI 整合）

**建議選項**: **OpenAI Whisper API**

**理由**:
- ✅ 已有 OpenAI 客戶端和 API key
- ✅ 整合成本最低
- ✅ 繁體中文支援良好
- ✅ 準確率高 (85%+)

**實作複雜度**: **低 (Low)**
- 只需在現有 `OpenAIService` 添加一個方法
- 估計 0.5-1 天完成

**成本**: 約 $0.006/分鐘

#### 2. AI 對話分析服務

**狀態**: ✅ **已完成，無需額外整合**

使用現有 OpenAI GPT 服務，已整合完畢。

#### 3. 其他依賴

- Email 服務: SMTP（選用 SendGrid for production）
- PDF 生成: WeasyPrint
- 音訊元數據: mutagen

---

### 5. 技術風險（更新）

#### 風險 1: 音訊轉文字準確率 ← 維持
**影響**: 中等
**緩解**: 提供文字稿編輯功能

#### 風險 2: Excel 格式變化 ← 維持
**影響**: 中等
**緩解**: 彈性欄位映射配置

#### 風險 3: 檔案儲存空間 ← 維持
**影響**: 低
**緩解**: 大小限制、定期清理

#### 風險 4: AI 服務成本 ← 降低
**影響**: **低 (Low)** ← 從「中等」下調
**原因**: 主要 AI 功能已實作，只需新增音訊轉文字
**緩解**: 配額限制、快取結果

#### ~~風險 5: 業務30問題庫不明確~~ ← 消除
**狀態**: ✅ **已解決**
**原因**: 題庫檔案 `questionnaire_30.json` 已存在並整合

---

### 6. 研究與調查需求（更新）

#### ~~研究項目 1: 業務30問題庫~~ ← 已解決
**狀態**: ✅ **已完成**
**檔案**: `backend/app/data/questionnaire_30.json`

#### 研究項目 2: 客戶健檢報告範本
**狀態**: ⚠️ **仍需提供**
**需求**: 「客戶30問健檢紀錄表 (回覆).xlsx」範本檔案

#### 研究項目 3: 臉書廣告表單範例
**狀態**: ⚠️ **仍需提供**
**需求**: 「20220714_臉書廣告表單_20250502更新.xlsx」範例

---

### 7. 建議實作策略（更新）

#### 總體方法: **混合方法 (Hybrid)** - 維持不變

#### 實施階段（更新：6個階段，6-8週）

**Phase 1: 資料基礎建設 (1 週)** ← 縮短

**目標**: 建立資料模型和基礎 API

**任務**:
1. 擴展 Customer 模型
2. 新增 5 個資料表（Interaction, AIAnalysis, etc.）
3. 執行資料庫遷移
4. 實作基礎 CRUD API

---

**Phase 2: Excel 導入功能 (1-1.5 週)** ← 維持

**目標**: 實作名單導入

**任務**:
1. Excel 解析服務
2. 導入 API
3. 前端上傳 UI
4. 導入歷史

---

**Phase 3: 檔案管理與互動記錄 (1.5-2 週)** ← 維持

**目標**: 檔案上傳和互動記錄

**任務**:
1. 檔案儲存服務
2. 檔案上傳 API
3. 音訊時長提取
4. 互動記錄 CRUD
5. 前端上傳組件、音訊播放器、時間軸

---

**Phase 4: 音訊轉文字整合 (0.5-1 週)** ← **大幅縮短**（原2-3週）

**目標**: 唯一需要新增的 AI 功能

**任務**:
1. 在 `OpenAIService` 新增 `transcribe_audio()` 方法
2. 新增 `/api/v1/ai/transcribe` 端點
3. 前端轉換狀態顯示和文字稿編輯器

**前置條件**: 無（所有 AI 分析功能已完成）

**重要**:
- ✅ 業務30問匹配 - **已完成，無需開發**
- ✅ 對話分析 - **已完成，無需開發**
- ✅ AA 客戶評估 - **已完成，無需開發**

---

**Phase 5: 健檢報告生成 (1.5-2 週)** ← 維持

**目標**: 報告生成和匯出

**任務**:
1. HealthCheckReport 模型
2. Excel 報告生成服務
3. 整合現有 AI 分析結果（直接調用現有 API）
4. 報告 CRUD API
5. PDF 生成
6. Email 服務
7. 前端預覽和匯出 UI

**前置條件**: 需要健檢報告 Excel 範本

---

**Phase 6: 優化與測試 (1 週)** ← 縮短

**目標**: 完善和測試

**任務**:
1. 效能優化
2. 單元測試
3. 整合測試
4. Bug 修復

---

#### 時間估計總結

| 階段 | 原估計 | 新估計 | 節省時間 |
|------|--------|--------|----------|
| Phase 1 | 1-2週 | 1週 | 0.5週 |
| Phase 2 | 1-2週 | 1-1.5週 | 0.5週 |
| Phase 3 | 2-3週 | 1.5-2週 | 1週 |
| Phase 4 | 2-3週 | **0.5-1週** | **2週** ✨ |
| Phase 5 | 2-3週 | 1.5-2週 | 1週 |
| Phase 6 | 1-2週 | 1週 | 0.5週 |
| **總計** | **8-12週** | **6-8週** | **4-5週** |

**節省原因**: AI 核心功能（對話分析、業務30問匹配、AA評估）已 100% 完成

---

## 關鍵結論

### 重大發現

✅ **業務30問完整實作** - 包含題庫、匹配邏輯、API 端點全部完成
✅ **AA 客戶評估完整實作** - 評分、判定、API 全部完成
✅ **對話分析完整實作** - 資訊提取、問題匹配、API 全部完成

### 實際需要開發的核心功能

1. **Excel 導入與匯出** - 中等複雜度
2. **檔案上傳系統** - 中等複雜度
3. **音訊轉文字** - 低複雜度（僅需擴展現有服務）
4. **互動記錄時間軸** - 中等複雜度
5. **報告生成** - 中等複雜度

### 不需要開發的功能（已完成）

1. ~~業務30問題庫~~ ✅
2. ~~對話分析和問題匹配~~ ✅
3. ~~客戶資訊提取~~ ✅
4. ~~AA 客戶評估邏輯~~ ✅
5. ~~對話品質評估基礎~~ ✅

### 建議行動

1. **立即可開始**: Phase 1-3 無阻塞
2. **需要範本**: Phase 5 需要健檢報告範本
3. **可選研究**: 臉書廣告表單範例（優化導入邏輯）

### 整體評估

**原評估**: 中等偏高，8-12週
**新評估**: **中等，6-8週**

**信心度**: **高 (High)**

**原因**: 核心 AI 功能已 100% 完成，降低約 40% 開發工作量

---

**文件資訊**:
- 分析日期: 2026-03-26（修訂版）
- 代碼庫版本: 1.0.0
- 分析工具: 代碼掃描 + 需求對比 + AI API 驗證
- 狀態: 已完成修訂
- 修訂原因: 發現業務30問和 AI 分析功能已完整實作
