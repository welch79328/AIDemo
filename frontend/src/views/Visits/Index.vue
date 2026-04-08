<template>
  <div class="visits-page">
    <!-- 頁面標題 -->
    <el-page-header @back="goBack" content="拜訪記錄" class="page-header" />

    <!-- 搜尋與操作列 -->
    <el-card class="search-card" shadow="never">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select v-model="filterCustomer" placeholder="選擇客戶" clearable filterable @change="handleSearch">
            <el-option
              v-for="customer in customers"
              :key="customer.id"
              :label="customer.company_name"
              :value="customer.id"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterType" placeholder="拜訪類型" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="一訪" value="first_visit" />
            <el-option label="二訪" value="second_visit" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterStatus" placeholder="拜訪狀態" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="已排程" value="scheduled" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-col>
        <el-col :span="10" style="text-align: right">
          <el-button type="primary" @click="handleCreate" :icon="Plus">新增拜訪記錄</el-button>
          <el-button @click="handleRefresh" :icon="Refresh">重新整理</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 統計卡片 -->
    <el-row :gutter="20" class="stats-row" v-if="statistics">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="總拜訪數" :value="statistics.total_visits">
            <template #prefix>
              <el-icon><DocumentCopy /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="一訪數量" :value="statistics.first_visits">
            <template #prefix>
              <el-icon style="color: #409eff"><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="二訪數量" :value="statistics.second_visits">
            <template #prefix>
              <el-icon style="color: #67c23a"><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="已完成" :value="statistics.completed_visits">
            <template #prefix>
              <el-icon style="color: #67c23a"><Select /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 拜訪記錄列表 -->
    <el-card class="table-card" shadow="never">
      <el-table
        :data="visitStore.visits"
        v-loading="visitStore.loading"
        stripe
        style="width: 100%"
      >
        <el-table-column label="客戶名稱" width="180">
          <template #default="{ row }">
            {{ getCustomerName(row.customer_id) }}
          </template>
        </el-table-column>
        <el-table-column label="拜訪類型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.visit_type === 'first_visit' ? 'primary' : 'success'" size="small">
              {{ row.visit_type === 'first_visit' ? '一訪' : '二訪' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="拜訪日期" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.visit_date) }}
          </template>
        </el-table-column>
        <el-table-column label="拜訪狀態" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.visit_status)" size="small">
              {{ getStatusLabel(row.visit_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="備註" min-width="200" show-overflow-tooltip />
        <el-table-column label="下次拜訪" width="180">
          <template #default="{ row }">
            <span v-if="row.next_visit_date">{{ formatDateTime(row.next_visit_date) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="建立時間" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEdit(row)">
              編輯
            </el-button>
            <el-button link type="info" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">
              刪除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分頁 -->
      <el-pagination
        v-model:current-page="visitStore.page"
        v-model:page-size="visitStore.limit"
        :page-sizes="[10, 20, 50, 100]"
        :total="visitStore.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        class="pagination"
      />
    </el-card>

    <!-- 新增/編輯對話框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="900px"
      top="5vh"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="客戶" prop="customer_id">
          <el-select v-model="formData.customer_id" placeholder="請選擇客戶" filterable>
            <el-option
              v-for="customer in customers"
              :key="customer.id"
              :label="customer.company_name"
              :value="customer.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="拜訪類型" prop="visit_type">
          <el-radio-group v-model="formData.visit_type">
            <el-radio value="first_visit">一訪</el-radio>
            <el-radio value="second_visit">二訪</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="拜訪日期" prop="visit_date">
          <el-date-picker
            v-model="formData.visit_date"
            type="datetime"
            placeholder="選擇日期時間"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="拜訪狀態" prop="visit_status">
          <el-radio-group v-model="formData.visit_status">
            <el-radio value="scheduled">已排程</el-radio>
            <el-radio value="completed">已完成</el-radio>
            <el-radio value="cancelled">已取消</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 完整 30 問問卷 -->
        <el-divider>
          <span>問卷資料（客戶健檢表 30 問）</span>
        </el-divider>

        <!-- AI 對談匯入功能 -->
        <el-card shadow="never" style="margin-bottom: 20px; background-color: #f0f9ff;">
          <template #header>
            <div style="display: flex; align-items: center; justify-content: space-between;">
              <span style="color: #409eff; font-weight: bold;">💡 AI 智能填寫</span>
              <el-button
                type="primary"
                size="small"
                @click="showConversationImport = true"
                :icon="Upload"
              >
                匯入對談記錄
              </el-button>
            </div>
          </template>
          <div style="font-size: 13px; color: #606266;">
            上傳拜訪對談記錄，AI 將自動分析並填寫匹配的問卷答案（不限一訪/二訪）
          </div>
        </el-card>

        <!-- 基本資訊問題 (1-10) -->
        <el-divider content-position="left">基本資訊（問題 1-10）</el-divider>
        <el-form-item label="1. 公司官網 FB 網站：">
            <el-radio-group v-model="questionnaireForm.q1_website">
              <el-radio value="N">無</el-radio>
              <el-radio value="Y">有</el-radio>
            </el-radio-group>
            <el-input
              v-if="questionnaireForm.q1_website === 'Y'"
              v-model="questionnaireForm.q1_link"
              placeholder="請輸入網址"
              style="margin-top: 10px"
            />
          </el-form-item>

          <el-form-item label="2. 是否有用LINE個人/ LINE OA 管理租客">
            <el-radio-group v-model="questionnaireForm.q2_line_type">
              <el-radio value="No">無</el-radio>
              <el-radio value="LINE個人">LINE個人</el-radio>
              <el-radio value="LINE OA">LINE OA</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="3. 公司/ 品牌名稱：">
            <el-input v-model="questionnaireForm.q3_company_name" placeholder="請輸入公司/品牌名稱" />
          </el-form-item>

          <el-form-item label="4. 公司/個人 經營階段：">
            <el-radio-group v-model="questionnaireForm.q4_business_stage">
              <el-radio value="a">個人戶</el-radio>
              <el-radio value="b">準備成立公司</el-radio>
              <el-radio value="c">剛成立公司</el-radio>
              <el-radio value="d">物件量增加想數位升級</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="5. 公司老闆/集團背景：(當初怎麼會想經營包租代管這個行業？)">
            <el-checkbox-group v-model="questionnaireForm.q5_background">
              <el-checkbox value="a">仲介</el-checkbox>
              <el-checkbox value="b">建設</el-checkbox>
              <el-checkbox value="c">家族/集團</el-checkbox>
              <el-checkbox value="d">室內裝修/工程</el-checkbox>
              <el-checkbox value="e">純包租代管/創業</el-checkbox>
              <el-checkbox value="f">旅館短租起家</el-checkbox>
              <el-checkbox value="g">斜槓兼職</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="6. 物件比例(包租 代管)">
            <el-input v-model="questionnaireForm.q6_property_ratio" placeholder="例：包租70%、代管30%" />
          </el-form-item>

          <el-form-item label="7. 客戶的案場規劃">
            <el-checkbox-group v-model="questionnaireForm.q7_property_types">
              <el-checkbox value="a">共生宅</el-checkbox>
              <el-checkbox value="b">套雅房</el-checkbox>
              <el-checkbox value="c">整層</el-checkbox>
              <el-checkbox value="d">透套</el-checkbox>
              <el-checkbox value="e">共享辦公室&商務中心</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="8. 公司分布地點 (分布 總部)">
            <el-input v-model="questionnaireForm.q8_locations" type="textarea" :rows="2" placeholder="請描述物件分布地區及總部位置" />
          </el-form-item>

          <el-form-item label="9. 是否有經營社宅">
            <el-radio-group v-model="questionnaireForm.q9_social_housing">
              <el-radio value="Y">是</el-radio>
              <el-radio value="N">否</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="10. 客戶目前的難題，最優先想解決之痛點">
            <el-input v-model="questionnaireForm.q10_pain_points" type="textarea" :rows="3" placeholder="客戶最優先想解決的問題" />
          </el-form-item>

        <!-- 進階資訊問題 (11-24) -->
        <el-divider content-position="left">進階資訊（問題 11-24）</el-divider>

          <el-form-item label="11. 是否有規劃擴大營運嗎？(或著即將有新接案場)">
            <el-radio-group v-model="questionnaireForm.q11_expansion">
              <el-radio value="Y">是（AA客戶）</el-radio>
              <el-radio value="N">否</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="12. 公司/決策者之目標">
            <el-checkbox-group v-model="questionnaireForm.q12_goals">
              <el-checkbox value="戶數增加">戶數增加</el-checkbox>
              <el-checkbox value="人員異動">人員異動</el-checkbox>
              <el-checkbox value="人力減少">人力減少</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="13. 公司組織人力數據(會計 業務 經理)">
            <el-row :gutter="10">
              <el-col :span="8">
                <el-input v-model="questionnaireForm.q13_total_properties" placeholder="總戶數" />
              </el-col>
              <el-col :span="8">
                <el-input v-model="questionnaireForm.q13_total_staff" placeholder="總人數" />
              </el-col>
              <el-col :span="8">
                <el-input v-model="questionnaireForm.q13_staff_division" placeholder="人員分工" />
              </el-col>
            </el-row>
          </el-form-item>

          <el-form-item label="14. (金流) 公司帳務方式(紙本 系統 外包會計人員)">
            <el-radio-group v-model="questionnaireForm.q14_accounting_method">
              <el-radio value="紙本">紙本</el-radio>
              <el-radio value="系統">系統</el-radio>
              <el-radio value="外包">外包會計人員</el-radio>
            </el-radio-group>
            <el-input v-model="questionnaireForm.q14_payment_details" type="textarea" :rows="2" placeholder="收帳方式、是否使用虛擬帳戶等" style="margin-top: 10px" />
          </el-form-item>

          <el-form-item label="15. (代管) 大房東數量">
            <el-input v-model="questionnaireForm.q15_landlord_count" placeholder="需同時回報幾位屋主" />
            <el-checkbox v-model="questionnaireForm.q15_monthly_report" label="每月需製作損益表給大房東（AA客戶）" style="margin-top: 10px" />
          </el-form-item>

          <el-form-item label="16. (包租) 是否大部分是包租物件? 每個月需要製作「差額發票」">
            <el-radio-group v-model="questionnaireForm.q16_invoice_needed">
              <el-radio value="Y">是（100-200戶以上為AA客戶）</el-radio>
              <el-radio value="N">否</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="17. (租客) 取向(高資產 中資產 低資產 類型)">
            <el-checkbox-group v-model="questionnaireForm.q17_tenant_types">
              <el-checkbox value="高資產">高資產</el-checkbox>
              <el-checkbox value="中資產">中資產</el-checkbox>
              <el-checkbox value="低資產">低資產</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="18. (租客) 是否有外籍租客?">
            <el-radio-group v-model="questionnaireForm.q18_foreign_tenants">
              <el-radio value="Y">是（AA客戶）</el-radio>
              <el-radio value="N">否</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="19. 是否有會計部門?幾個人">
            <el-row :gutter="10">
              <el-col :span="12">
                <el-radio-group v-model="questionnaireForm.q19_has_accounting">
                  <el-radio value="Y">有</el-radio>
                  <el-radio value="N">無</el-radio>
                </el-radio-group>
              </el-col>
              <el-col :span="12">
                <el-input v-if="questionnaireForm.q19_has_accounting === 'Y'" v-model="questionnaireForm.q19_accounting_staff" placeholder="人數" />
              </el-col>
            </el-row>
          </el-form-item>

          <el-form-item label="20. 公司作業方式(紙本 系統) / 是否有用其他協力系統?">
            <el-radio-group v-model="questionnaireForm.q20_operation_method">
              <el-radio value="紙本">紙本</el-radio>
              <el-radio value="系統">系統</el-radio>
            </el-radio-group>
            <el-input v-model="questionnaireForm.q20_other_systems" placeholder="是否使用其他協力系統" style="margin-top: 10px" />
          </el-form-item>

          <el-form-item label="21. 是否有自己的官網 (是否有興趣花5000元製作一個形象官網，可以5種套版選一種)">
            <el-radio-group v-model="questionnaireForm.q21_website_interest">
              <el-radio value="Y">有興趣（5000元形象官網）</el-radio>
              <el-radio value="N">無</el-radio>
              <el-radio value="已有">已有官網</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="22. 客戶目前的競品(相同性質)">
            <el-checkbox-group v-model="questionnaireForm.q22_competitors">
              <el-checkbox value="飛豬">飛豬</el-checkbox>
              <el-checkbox value="DDROOM">DDROOM</el-checkbox>
              <el-checkbox value="包管家">包管家</el-checkbox>
              <el-checkbox value="其他">其他</el-checkbox>
            </el-checkbox-group>
            <el-input v-model="questionnaireForm.q22_other_competitor" placeholder="其他競品" style="margin-top: 10px" />
          </el-form-item>

          <el-form-item label="23. LINE 拉群/ 唐三藏：">
            <el-radio-group v-model="questionnaireForm.q23_line_group">
              <el-radio value="Y">是</el-radio>
              <el-radio value="N">否</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="24. 公司決策人員：">
            <el-input v-model="questionnaireForm.q24_decision_makers" placeholder="請輸入決策人員資訊" />
          </el-form-item>

        <el-divider />
        <el-form-item label="備註">
          <el-input v-model="formData.notes" type="textarea" :rows="3" placeholder="請輸入備註" />
        </el-form-item>
        <el-form-item label="下一步行動">
          <el-input v-model="formData.next_action" placeholder="請輸入下一步行動" />
        </el-form-item>
        <el-form-item label="下次拜訪日期">
          <el-date-picker
            v-model="formData.next_visit_date"
            type="datetime"
            placeholder="選擇日期時間"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="visitStore.loading">
          確定
        </el-button>
      </template>
    </el-dialog>

    <!-- AI 對談匯入對話框（兩步驟） -->
    <el-dialog
      v-model="showConversationImport"
      :title="aiStep === 'input' ? '匯入對談記錄 - AI 智能填寫問卷' : 'AI 分析結果預覽'"
      :width="aiStep === 'input' ? '700px' : '900px'"
      :close-on-click-modal="false"
      @close="handleAIDialogClose"
    >
      <!-- Step 1: 輸入 -->
      <div v-if="aiStep === 'input'">
        <el-alert
          title="如何使用"
          type="info"
          :closable="false"
          style="margin-bottom: 15px;"
        >
          <div>1. 貼上或上傳拜訪對談記錄</div>
          <div>2. 點擊「AI 分析」按鈕</div>
          <div>3. 預覽分析結果後，勾選要填入的項目</div>
        </el-alert>

        <el-input
          v-model="conversationText"
          type="textarea"
          :rows="12"
          placeholder="請貼上對談記錄...&#10;&#10;範例：&#10;你&#10; 你們現在大概幾間啊？&#10;業者&#10; 一百多。"
        />

        <el-divider>或</el-divider>

        <el-upload
          class="upload-demo"
          drag
          :auto-upload="false"
          :on-change="handleConversationFileChange"
          :show-file-list="false"
          accept=".txt"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖曳文件或<em>點擊上傳</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">支援 .txt 文件</div>
          </template>
        </el-upload>
      </div>

      <!-- Step 2: 結果預覽 -->
      <div v-else-if="aiStep === 'result'" class="ai-result-preview">
        <!-- 摘要 -->
        <el-card shadow="never" style="margin-bottom: 16px;">
          <template #header>
            <span style="font-weight: bold;">📊 分析摘要</span>
          </template>
          <p style="margin: 0; color: #606266; line-height: 1.6;">{{ aiResultCache?.summary }}</p>
        </el-card>

        <!-- AA 客戶評估 -->
        <el-card v-if="aiStore.aaAssessment" shadow="never" style="margin-bottom: 16px;">
          <template #header>
            <div style="display: flex; align-items: center; justify-content: space-between;">
              <span style="font-weight: bold;">⭐ AA 客戶評估</span>
              <el-tag :type="aiStore.aaAssessment.is_aa_customer ? 'success' : 'info'" size="large">
                {{ aiStore.aaAssessment.is_aa_customer ? 'AA 客戶' : '非 AA 客戶' }}
              </el-tag>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="8">
              <div style="text-align: center;">
                <div style="color: #909399; margin-bottom: 8px;">評分</div>
                <el-progress
                  type="circle"
                  :width="80"
                  :percentage="aiStore.aaAssessment.score"
                  :color="getAAScoreColor(aiStore.aaAssessment.score)"
                />
              </div>
            </el-col>
            <el-col :span="8">
              <div style="text-align: center;">
                <div style="color: #909399; margin-bottom: 8px;">信心度</div>
                <el-progress
                  type="circle"
                  :width="80"
                  :percentage="aiStore.aaAssessment.confidence"
                  color="#409eff"
                />
              </div>
            </el-col>
            <el-col :span="8">
              <div style="padding-top: 8px;">
                <div style="color: #909399; margin-bottom: 8px;">判定原因</div>
                <ul style="margin: 0; padding-left: 16px; font-size: 13px; color: #606266;">
                  <li v-for="(reason, idx) in aiStore.aaAssessment.reasons" :key="idx">{{ reason }}</li>
                </ul>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 客戶資訊 -->
        <el-card v-if="aiResultCache?.customer_info" shadow="never" style="margin-bottom: 16px;">
          <template #header>
            <span style="font-weight: bold;">👤 客戶基本資訊</span>
          </template>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="公司名稱">
              {{ aiResultCache.customer_info.company_name || '未提及' }}
            </el-descriptions-item>
            <el-descriptions-item label="業務類型">
              {{ aiResultCache.customer_info.business_type || '未知' }}
            </el-descriptions-item>
            <el-descriptions-item label="物件數量">
              <el-tag v-if="aiResultCache.customer_info.property_count" type="success">
                {{ aiResultCache.customer_info.property_count }} 間
              </el-tag>
              <span v-else>未提及</span>
            </el-descriptions-item>
            <el-descriptions-item label="人員數量">
              <el-tag v-if="aiResultCache.customer_info.staff_count" type="info">
                {{ aiResultCache.customer_info.staff_count }} 人
              </el-tag>
              <span v-else>未提及</span>
            </el-descriptions-item>
          </el-descriptions>
          <div v-if="aiResultCache.customer_info.pain_points?.length" style="margin-top: 12px;">
            <span style="color: #909399; font-size: 13px;">痛點：</span>
            <el-tag
              v-for="(point, idx) in aiResultCache.customer_info.pain_points"
              :key="idx"
              type="warning"
              size="small"
              style="margin: 4px;"
            >{{ point }}</el-tag>
          </div>
        </el-card>

        <!-- 匹配問題（可勾選） -->
        <el-card shadow="never">
          <template #header>
            <div style="display: flex; align-items: center; justify-content: space-between;">
              <span style="font-weight: bold;">✅ 匹配的問卷問題</span>
              <div>
                <el-button size="small" @click="toggleAllQuestions(true)">全選</el-button>
                <el-button size="small" @click="toggleAllQuestions(false)">取消全選</el-button>
                <el-tag type="success" style="margin-left: 8px;">
                  {{ selectedQuestionIndices.length }} / {{ aiResultCache?.matched_questions.length }} 題
                </el-tag>
              </div>
            </div>
          </template>
          <el-table
            :data="aiResultCache?.matched_questions || []"
            style="width: 100%"
            max-height="400"
            @selection-change="handleQuestionSelectionChange"
            ref="questionTableRef"
          >
            <el-table-column type="selection" width="45" />
            <el-table-column label="題號" width="65">
              <template #default="{ row }">
                <el-tag size="small">Q{{ row.question_number }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="問題" prop="question_text" min-width="200" show-overflow-tooltip />
            <el-table-column label="答案" prop="answer" min-width="180" show-overflow-tooltip />
            <el-table-column label="信心度" width="100" sortable>
              <template #default="{ row }">
                <el-tag
                  :type="row.confidence >= 80 ? 'success' : row.confidence >= 50 ? 'warning' : 'danger'"
                  size="small"
                >
                  {{ row.confidence }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="證據" prop="evidence" min-width="150" show-overflow-tooltip />
          </el-table>
        </el-card>
      </div>

      <template #footer>
        <template v-if="aiStep === 'input'">
          <el-button @click="showConversationImport = false">取消</el-button>
          <el-button
            type="primary"
            @click="handleAIAnalyze"
            :loading="aiAnalyzing"
          >
            <el-icon><MagicStick /></el-icon>
            AI 分析
          </el-button>
        </template>
        <template v-else>
          <el-button @click="aiStep = 'input'">返回修改</el-button>
          <el-button @click="showConversationImport = false">取消</el-button>
          <el-button
            type="primary"
            @click="handleConfirmImport"
          >
            確認填入問卷（{{ selectedQuestionIndices.length }} 題）
          </el-button>
        </template>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, DocumentCopy, Document, Select, Upload, UploadFilled, MagicStick } from '@element-plus/icons-vue'
import { useVisitStore } from '@/stores/visit'
import { useCustomerStore } from '@/stores/customer'
import { useAIStore } from '@/stores/ai'
import type { VisitListItem, VisitCreateRequest, VisitUpdateRequest } from '@/api/visit'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'

const router = useRouter()
const visitStore = useVisitStore()
const customerStore = useCustomerStore()
const aiStore = useAIStore()

// 篩選條件
const filterCustomer = ref('')
const filterType = ref('')
const filterStatus = ref('')

// 客戶列表
const customers = ref<any[]>([])

// 統計資料
const statistics = ref(null)

// 對話框
const dialogVisible = ref(false)
const dialogTitle = ref('新增拜訪記錄')
const dialogMode = ref<'create' | 'edit'>('create')
const currentEditId = ref('')

// AI 對談匯入（兩步驟）
const showConversationImport = ref(false)
const conversationText = ref('')
const aiAnalyzing = ref(false)
const aiStep = ref<'input' | 'result'>('input')
const aiResultCache = ref<any>(null)
const selectedQuestionIndices = ref<any[]>([])
const questionTableRef = ref<any>(null)

// 表單
const formRef = ref<FormInstance>()
const formData = ref<VisitCreateRequest & VisitUpdateRequest>({
  customer_id: '',
  visit_type: 'first_visit' as any,
  visit_date: '',
  visit_status: 'scheduled' as any,
  notes: '',
  next_action: '',
  next_visit_date: ''
})

// 完整問卷資料 (24 問) - 對齊 questionnaire_30.json
const questionnaireForm = reactive<Record<string, any>>({
  // 基本資訊 (1-10)
  q1_website: '',
  q1_link: '',
  q2_line_type: '',
  q3_company_name: '',
  q4_business_stage: '',
  q5_background: [],
  q6_property_ratio: '',
  q7_property_types: [],
  q8_locations: '',
  q9_social_housing: '',
  q10_pain_points: '',
  // 進階資訊 (11-24)
  q11_expansion: '',
  q12_goals: [],
  q13_total_properties: '',
  q13_total_staff: '',
  q13_staff_division: '',
  q14_accounting_method: '',
  q14_payment_details: '',
  q15_landlord_count: '',
  q15_monthly_report: false,
  q16_invoice_needed: '',
  q17_tenant_types: [],
  q18_foreign_tenants: '',
  q19_has_accounting: '',
  q19_accounting_staff: '',
  q20_operation_method: '',
  q20_other_systems: '',
  q21_website_interest: '',
  q22_competitors: [],
  q22_other_competitor: '',
  q23_line_group: '',
  q24_decision_makers: ''
})

const formRules: FormRules = {
  customer_id: [
    { required: true, message: '請選擇客戶', trigger: 'change' }
  ],
  visit_type: [
    { required: true, message: '請選擇拜訪類型', trigger: 'change' }
  ],
  visit_date: [
    { required: true, message: '請選擇拜訪日期', trigger: 'change' }
  ]
}

// 載入資料
onMounted(async () => {
  await loadCustomers()
  await loadData()
  await loadStatistics()
})

async function loadCustomers() {
  await customerStore.fetchCustomers({ limit: 100 })
  customers.value = customerStore.customers
}

async function loadData() {
  const params: any = {}
  if (filterCustomer.value) params.customer_id = filterCustomer.value
  if (filterType.value) params.visit_type = filterType.value
  if (filterStatus.value) params.visit_status = filterStatus.value

  await visitStore.fetchVisits(params)
}

async function loadStatistics() {
  statistics.value = await visitStore.fetchStatistics() as any
}

// 搜尋
function handleSearch() {
  visitStore.setPage(1)
  loadData()
}

// 重新整理
async function handleRefresh() {
  filterCustomer.value = ''
  filterType.value = ''
  filterStatus.value = ''
  visitStore.setPage(1)
  await loadData()
  await loadStatistics()
}

// 分頁
function handleSizeChange(size: number) {
  visitStore.setLimit(size)
  loadData()
}

function handlePageChange(page: number) {
  visitStore.setPage(page)
  loadData()
}

// 新增拜訪記錄
function handleCreate() {
  dialogMode.value = 'create'
  dialogTitle.value = '新增拜訪記錄'
  formData.value = {
    customer_id: '',
    visit_type: 'first_visit' as any,
    visit_date: '',
    visit_status: 'scheduled' as any,
    notes: '',
    next_action: '',
    next_visit_date: ''
  }
  // 清空問卷所有欄位
  resetQuestionnaireForm()
  dialogVisible.value = true
}

// 重置問卷表單
function resetQuestionnaireForm() {
  // 基本資訊 (1-10)
  questionnaireForm.q1_website = ''
  questionnaireForm.q1_link = ''
  questionnaireForm.q2_line_type = ''
  questionnaireForm.q3_company_name = ''
  questionnaireForm.q4_business_stage = ''
  questionnaireForm.q5_background = []
  questionnaireForm.q6_property_ratio = ''
  questionnaireForm.q7_property_types = []
  questionnaireForm.q8_locations = ''
  questionnaireForm.q9_social_housing = ''
  questionnaireForm.q10_pain_points = ''
  // 進階資訊 (11-24)
  questionnaireForm.q11_expansion = ''
  questionnaireForm.q12_goals = []
  questionnaireForm.q13_total_properties = ''
  questionnaireForm.q13_total_staff = ''
  questionnaireForm.q13_staff_division = ''
  questionnaireForm.q14_accounting_method = ''
  questionnaireForm.q14_payment_details = ''
  questionnaireForm.q15_landlord_count = ''
  questionnaireForm.q15_monthly_report = false
  questionnaireForm.q16_invoice_needed = ''
  questionnaireForm.q17_tenant_types = []
  questionnaireForm.q18_foreign_tenants = ''
  questionnaireForm.q19_has_accounting = ''
  questionnaireForm.q19_accounting_staff = ''
  questionnaireForm.q20_operation_method = ''
  questionnaireForm.q20_other_systems = ''
  questionnaireForm.q21_website_interest = ''
  questionnaireForm.q22_competitors = []
  questionnaireForm.q22_other_competitor = ''
  questionnaireForm.q23_line_group = ''
  questionnaireForm.q24_decision_makers = ''
}

// 編輯拜訪記錄
function handleEdit(row: VisitListItem) {
  dialogMode.value = 'edit'
  dialogTitle.value = '編輯拜訪記錄'
  currentEditId.value = row.id
  formData.value = {
    customer_id: row.customer_id,
    visit_type: row.visit_type,
    visit_date: row.visit_date,
    visit_status: row.visit_status,
    notes: row.notes || '',
    next_visit_date: row.next_visit_date || ''
  }

  // 載入問卷資料
  resetQuestionnaireForm()
  if (row.questionnaire_data) {
    Object.assign(questionnaireForm, row.questionnaire_data)
  }

  dialogVisible.value = true
}

// 查看拜訪記錄
function handleView(row: VisitListItem) {
  router.push(`/visits/${row.id}`)
}

// 刪除拜訪記錄
async function handleDelete(row: VisitListItem) {
  try {
    await ElMessageBox.confirm(
      `確定要刪除此拜訪記錄嗎？`,
      '刪除確認',
      {
        confirmButtonText: '確定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await visitStore.deleteVisit(row.id)
    await loadStatistics()
  } catch (error) {
    // 取消刪除
  }
}

// 提交表單
async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 組合問卷資料 - 過濾掉空值，直接複製所有非空欄位
        const questionnaire: Record<string, any> = {}

        // 遍歷所有問卷欄位，過濾空值
        Object.keys(questionnaireForm).forEach((key) => {
          const value = questionnaireForm[key]
          // 檢查是否有值（字串非空、陣列有元素、布林值為 true）
          if (value) {
            if (typeof value === 'string' && value.trim()) {
              questionnaire[key] = value
            } else if (Array.isArray(value) && value.length > 0) {
              questionnaire[key] = value
            } else if (typeof value === 'boolean') {
              questionnaire[key] = value
            }
          }
        })

        // 準備提交資料，過濾空的日期欄位
        const submitData: any = {
          customer_id: formData.value.customer_id,
          visit_type: formData.value.visit_type,
          visit_date: formData.value.visit_date,
          visit_status: formData.value.visit_status,
          questionnaire_data: Object.keys(questionnaire).length > 0 ? questionnaire : undefined
        }

        // 只在有值時才加入這些可選欄位
        if (formData.value.notes && formData.value.notes.trim()) {
          submitData.notes = formData.value.notes
        }
        if (formData.value.next_action && formData.value.next_action.trim()) {
          submitData.next_action = formData.value.next_action
        }
        if (formData.value.next_visit_date) {
          submitData.next_visit_date = formData.value.next_visit_date
        }

        if (dialogMode.value === 'create') {
          await visitStore.createVisit(submitData)
        } else {
          await visitStore.updateVisit(currentEditId.value, submitData)
        }
        dialogVisible.value = false
        await loadStatistics()
      } catch (error) {
        // 錯誤已在 store 中處理
      }
    }
  })
}

// 關閉對話框
function handleDialogClose() {
  formRef.value?.resetFields()
}

// 返回
function goBack() {
  router.back()
}

// 輔助函數
function getCustomerName(customerId: string): string {
  const customer = customers.value.find(c => c.id === customerId)
  return customer ? customer.company_name : '未知客戶'
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    scheduled: '已排程',
    completed: '已完成',
    cancelled: '已取消'
  }
  return labels[status] || status
}

function getStatusTagType(status: string): string {
  const types: Record<string, any> = {
    scheduled: 'info',
    completed: 'success',
    cancelled: 'danger'
  }
  return types[status] || ''
}

function formatDateTime(dateString: string): string {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-TW')
}

// AI 對談分析相關函數
function handleConversationFileChange(file: UploadFile) {
  const reader = new FileReader()
  reader.onload = (e) => {
    conversationText.value = e.target?.result as string
    ElMessage.success('文件載入成功')
  }
  reader.readAsText(file.raw!)
}

async function handleAIAnalyze() {
  if (!conversationText.value.trim()) {
    ElMessage.warning('請輸入對談記錄')
    return
  }

  aiAnalyzing.value = true
  try {
    // 調用 AI 分析（不自動填入，先顯示結果）
    const result = await aiStore.analyzeConversation(conversationText.value)
    aiResultCache.value = result

    // 切換到結果預覽步驟
    aiStep.value = 'result'

    // 預設全選所有匹配問題
    setTimeout(() => {
      if (questionTableRef.value) {
        result.matched_questions.forEach((row: any) => {
          questionTableRef.value.toggleRowSelection(row, true)
        })
      }
    }, 100)

    ElMessage.success(`AI 分析完成！匹配 ${result.matched_questions.length} 個問題，請確認後填入`)
  } catch (error) {
    ElMessage.error('AI 分析失敗，請稍後再試')
  } finally {
    aiAnalyzing.value = false
  }
}

// 確認填入選取的問題
function handleConfirmImport() {
  if (selectedQuestionIndices.value.length > 0) {
    mapAIResultToQuestionnaire(selectedQuestionIndices.value)
  }

  // 填入客戶基本資訊
  if (aiResultCache.value?.customer_info) {
    fillCustomerInfo(aiResultCache.value.customer_info)
  }

  ElMessage.success(`已填入 ${selectedQuestionIndices.value.length} 個問題的答案`)
  showConversationImport.value = false
}

// 問題勾選變更
function handleQuestionSelectionChange(selection: any[]) {
  selectedQuestionIndices.value = selection
}

// 全選 / 取消全選
function toggleAllQuestions(selectAll: boolean) {
  if (!questionTableRef.value || !aiResultCache.value?.matched_questions) return
  if (selectAll) {
    aiResultCache.value.matched_questions.forEach((row: any) => {
      questionTableRef.value.toggleRowSelection(row, true)
    })
  } else {
    questionTableRef.value.clearSelection()
  }
}

// AA 評估分數顏色
function getAAScoreColor(score: number): string {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

// AI 對話框關閉時重置
function handleAIDialogClose() {
  aiStep.value = 'input'
  aiResultCache.value = null
  selectedQuestionIndices.value = []
  conversationText.value = ''
}

// 將 AI 分析結果映射到問卷表單（根據問題文本智能判斷）
function mapAIResultToQuestionnaire(matchedQuestions: any[]) {
  matchedQuestions.forEach((q) => {
    const questionText = q.question_text || ''
    const answer = q.answer

    // 根據問題文本內容來判斷應該填入哪個欄位
    if (questionText.includes('官網') || questionText.includes('FB')) {
      // Q1: 官網/FB
      // 判斷是否有官網或 FB
      if (answer.includes('FB') || answer.includes('粉專') || answer.includes('粉絲頁') ||
          answer.toLowerCase().includes('有') || answer.toLowerCase().includes('yes') ||
          answer.match(/https?:\/\//)) {
        questionnaireForm.q1_website = 'Y'
        // 嘗試提取網址
        const urlMatch = answer.match(/(https?:\/\/[^\s,，。]+)/)
        if (urlMatch) {
          questionnaireForm.q1_link = urlMatch[1]
        }
      } else if (answer.includes('無') || answer.includes('沒有') || answer.toLowerCase().includes('no')) {
        questionnaireForm.q1_website = 'N'
      }
    } else if (questionText.includes('LINE')) {
      // Q2: LINE 管理
      if (answer.includes('LINE OA')) questionnaireForm.q2_line_type = 'LINE OA'
      else if (answer.includes('LINE個人') || answer.includes('LINE')) questionnaireForm.q2_line_type = 'LINE個人'
      else questionnaireForm.q2_line_type = 'No'
    } else if (questionText.includes('公司') && questionText.includes('名稱')) {
      // Q3: 公司名稱
      questionnaireForm.q3_company_name = answer
    } else if (questionText.includes('經營階段')) {
      // Q4: 經營階段
      if (answer.includes('個人戶')) questionnaireForm.q4_business_stage = 'a'
      else if (answer.includes('準備成立')) questionnaireForm.q4_business_stage = 'b'
      else if (answer.includes('剛成立')) questionnaireForm.q4_business_stage = 'c'
      else if (answer.includes('數位升級')) questionnaireForm.q4_business_stage = 'd'
    } else if (questionText.includes('背景')) {
      // Q5: 公司背景
      const backgrounds: string[] = []
      if (answer.includes('仲介')) backgrounds.push('a')
      if (answer.includes('建設')) backgrounds.push('b')
      if (answer.includes('家族') || answer.includes('集團')) backgrounds.push('c')
      if (answer.includes('裝修') || answer.includes('工程')) backgrounds.push('d')
      if (answer.includes('包租代管') || answer.includes('創業')) backgrounds.push('e')
      if (answer.includes('旅館') || answer.includes('短租')) backgrounds.push('f')
      if (answer.includes('斜槓') || answer.includes('兼職')) backgrounds.push('g')
      questionnaireForm.q5_background = backgrounds
    } else if (questionText.includes('物件比例') || (questionText.includes('包租') && questionText.includes('代管') && !questionText.includes('發票'))) {
      // Q6: 物件比例
      questionnaireForm.q6_property_ratio = answer
    } else if (questionText.includes('案場') || questionText.includes('規劃')) {
      // Q7: 案場規劃
      const types: string[] = []
      if (answer.includes('共生宅')) types.push('a')
      if (answer.includes('套雅房') || answer.includes('套房')) types.push('b')
      if (answer.includes('整層')) types.push('c')
      if (answer.includes('透套')) types.push('d')
      if (answer.includes('共享辦公') || answer.includes('商務中心')) types.push('e')
      questionnaireForm.q7_property_types = types
    } else if (questionText.includes('分布') || questionText.includes('地點')) {
      // Q8: 分布地點
      questionnaireForm.q8_locations = answer
    } else if (questionText.includes('社宅')) {
      // Q9: 社宅
      questionnaireForm.q9_social_housing = answer.includes('有') || answer.includes('是') ? 'Y' : 'N'
    } else if (questionText.includes('痛點') || questionText.includes('難題')) {
      // Q10: 主要痛點
      questionnaireForm.q10_pain_points = answer
    } else if (questionText.includes('擴大營運') || questionText.includes('新接案場')) {
      // Q11: 規劃擴大營運
      questionnaireForm.q11_expansion = answer.includes('有') || answer.includes('是') ? 'Y' : 'N'
    } else if (questionText.includes('決策') && questionText.includes('目標')) {
      // Q12: 公司/決策者目標
      const goals: string[] = []
      if (answer.includes('戶數增加')) goals.push('戶數增加')
      if (answer.includes('人員異動')) goals.push('人員異動')
      if (answer.includes('人力減少')) goals.push('人力減少')
      questionnaireForm.q12_goals = goals
    } else if (questionText.includes('組織人力') || questionText.includes('人力數據')) {
      // Q13: 組織人力數據
      // 提取物件數量
      const propertyMatch = answer.match(/(\d+)\s*(?:間|戶|物件)/)
      if (propertyMatch) questionnaireForm.q13_total_properties = propertyMatch[1]

      // 提取人員數量（避免和物件數量混淆）
      const staffMatch = answer.match(/(\d+)\s*(?:人|位|個人)/)
      if (staffMatch && !answer.substring(answer.indexOf(staffMatch[0]) - 5, answer.indexOf(staffMatch[0])).includes('間')) {
        questionnaireForm.q13_total_staff = staffMatch[1]
      }

      // 保存完整描述作為人員分工
      questionnaireForm.q13_staff_division = answer
    } else if (questionText.includes('帳務') || questionText.includes('金流')) {
      // Q14: 帳務方式
      if (answer.includes('紙本')) {
        questionnaireForm.q14_accounting_method = '紙本'
      } else if (answer.includes('外包')) {
        questionnaireForm.q14_accounting_method = '外包'
      } else if (answer.includes('系統')) {
        questionnaireForm.q14_accounting_method = '系統'
      }
      // 保存完整回答作為詳細說明
      questionnaireForm.q14_payment_details = answer
    } else if (questionText.includes('大房東')) {
      // Q15: 大房東數量
      // 提取房東數量
      const landlordMatch = answer.match(/(\d+)\s*(?:個|位|間)/)
      if (landlordMatch) {
        questionnaireForm.q15_landlord_count = landlordMatch[1]
      } else {
        questionnaireForm.q15_landlord_count = answer
      }
      // 判斷是否需要做損益表
      questionnaireForm.q15_monthly_report = answer.includes('損益表') || answer.includes('報表')
    } else if (questionText.includes('差額發票')) {
      // Q16: 差額發票
      questionnaireForm.q16_invoice_needed = answer.includes('有') || answer.includes('是') ? 'Y' : 'N'
    } else if (questionText.includes('租客') && questionText.includes('取向')) {
      // Q17: 租客取向
      const types: string[] = []
      if (answer.includes('高資產')) types.push('高資產')
      if (answer.includes('中資產')) types.push('中資產')
      if (answer.includes('低資產')) types.push('低資產')
      questionnaireForm.q17_tenant_types = types
    } else if (questionText.includes('外籍')) {
      // Q18: 外籍租客
      questionnaireForm.q18_foreign_tenants = answer.includes('有') || answer.includes('是') ? 'Y' : 'N'
    } else if (questionText.includes('會計部門')) {
      // Q19: 會計部門
      if (answer.includes('有') || answer.includes('是') ||
          answer.match(/\d+\s*(?:人|位)/) ||
          answer.match(/[一二三四五六七八九十兩]+\s*(?:個)?(?:人|位)/)) {
        questionnaireForm.q19_has_accounting = 'Y'
        // 先嘗試提取阿拉伯數字
        let staffMatch = answer.match(/(\d+)\s*(?:人|位)/)
        if (staffMatch) {
          questionnaireForm.q19_accounting_staff = staffMatch[1]
        } else {
          // 嘗試提取中文數字並轉換
          const chineseMatch = answer.match(/(一|二|三|四|五|六|七|八|九|十|兩)\s*(?:個)?(?:人|位)/)
          if (chineseMatch) {
            const chineseToNumber = {'一': '1', '二': '2', '兩': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'}
            questionnaireForm.q19_accounting_staff = chineseToNumber[chineseMatch[1]] || chineseMatch[1]
          }
        }
      } else if (answer.includes('無') || answer.includes('沒有') || answer.includes('否')) {
        questionnaireForm.q19_has_accounting = 'N'
      }
    } else if (questionText.includes('作業方式') || questionText.includes('協力系統')) {
      // Q20: 作業方式
      if (answer.includes('紙本')) {
        questionnaireForm.q20_operation_method = '紙本'
      } else if (answer.includes('系統')) {
        questionnaireForm.q20_operation_method = '系統'
      }
      // 保存完整回答，可能包含其他系統資訊
      questionnaireForm.q20_other_systems = answer
    } else if (questionText.includes('官網') && (questionText.includes('需求') || questionText.includes('興趣') || questionText.includes('5000'))) {
      // Q21: 官網需求
      if (answer.includes('有興趣') || answer.includes('可以')) {
        questionnaireForm.q21_website_interest = 'Y'
      } else if (answer.includes('已有') || answer.includes('有官網')) {
        questionnaireForm.q21_website_interest = '已有'
      } else if (answer.includes('沒') || answer.includes('無')) {
        questionnaireForm.q21_website_interest = 'N'
      }
    } else if (questionText.includes('競品')) {
      // Q22: 競品
      const competitors: string[] = []
      if (answer.includes('飛豬')) competitors.push('飛豬')
      if (answer.includes('DDROOM')) competitors.push('DDROOM')
      if (answer.includes('包管家')) competitors.push('包管家')
      if (answer.includes('其他') && !competitors.length) competitors.push('其他')
      questionnaireForm.q22_competitors = competitors
      // 如果有提到具體的其他系統名稱，記錄下來
      if (answer.length > 0) {
        questionnaireForm.q22_other_competitor = answer
      }
    } else if (questionText.includes('拉群') || questionText.includes('唐三藏')) {
      // Q23: LINE 拉群/唐三藏
      questionnaireForm.q23_line_group = answer.includes('有') || answer.includes('是') ? 'Y' : 'N'
    } else if (questionText.includes('決策人員') && !questionText.includes('目標')) {
      // Q24: 公司決策人員
      questionnaireForm.q24_decision_makers = answer
    }
  })
}

// 填入客戶基本資訊
function fillCustomerInfo(customerInfo: any) {
  // 如果有公司名稱，填入問卷
  if (customerInfo.company_name) {
    questionnaireForm.q3_company_name = customerInfo.company_name
  }

  // 如果有物件數量，填入對應欄位 (Q13)
  if (customerInfo.property_count) {
    questionnaireForm.q13_total_properties = customerInfo.property_count.toString()
  }

  // 如果有人員數量 (Q13)
  if (customerInfo.staff_count) {
    questionnaireForm.q13_total_staff = customerInfo.staff_count.toString()
  }

  // 如果有業務類型
  if (customerInfo.business_type) {
    questionnaireForm.q6_property_ratio = customerInfo.business_type
  }

  // 如果有痛點
  if (customerInfo.pain_points && customerInfo.pain_points.length > 0) {
    questionnaireForm.q10_pain_points = customerInfo.pain_points.join('、')
  }
}
</script>

<style scoped>
.visits-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 問卷表單樣式 */
:deep(.el-dialog__body) {
  max-height: 70vh;
  overflow-y: auto;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

:deep(.el-divider__text) {
  font-weight: bold;
  color: #409eff;
}

:deep(.el-checkbox-group),
:deep(.el-radio-group) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

:deep(.el-checkbox),
:deep(.el-radio) {
  margin-right: 0;
}
</style>
