# API 設計文件

## API 概述

### 基本資訊
- **Base URL**: `https://api.sales-performance.com/v1`
- **認證方式**: JWT Bearer Token
- **資料格式**: JSON
- **字元編碼**: UTF-8

### 通用回應格式

#### 成功回應
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功",
  "timestamp": "2026-03-20T10:30:00Z"
}
```

#### 錯誤回應
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "輸入資料驗證失敗",
    "details": [
      {
        "field": "email",
        "message": "電子郵件格式不正確"
      }
    ]
  },
  "timestamp": "2026-03-20T10:30:00Z"
}
```

### HTTP 狀態碼
- `200 OK` - 請求成功
- `201 Created` - 資源建立成功
- `400 Bad Request` - 請求參數錯誤
- `401 Unauthorized` - 未認證
- `403 Forbidden` - 權限不足
- `404 Not Found` - 資源不存在
- `500 Internal Server Error` - 伺服器錯誤

---

## 認證 API

### 1. 註冊
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "sales@example.com",
  "password": "SecurePassword123!",
  "name": "王小明",
  "team": "台北團隊"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "sales@example.com",
      "name": "王小明",
      "role": "SALES"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 2. 登入
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "sales@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "sales@example.com",
      "name": "王小明",
      "role": "SALES",
      "team": "台北團隊"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": "7d"
  }
}
```

---

## 客戶管理 API

### 1. 取得客戶列表
```http
GET /customers?page=1&limit=20&status=FIRST_VISIT_DONE&isAa=true
```

**Query Parameters:**
- `page` (number): 頁碼，預設 1
- `limit` (number): 每頁筆數，預設 20，最大 100
- `status` (CustomerStatus): 篩選狀態
- `isAa` (boolean): 是否為 AA 客戶
- `search` (string): 搜尋公司名稱或聯絡人
- `sortBy` (string): 排序欄位，預設 `createdAt`
- `order` (asc|desc): 排序方向，預設 `desc`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "customers": [
      {
        "id": "uuid",
        "companyName": "XX 包租代管公司",
        "contactPerson": "張經理",
        "contactPhone": "0912-345-678",
        "contactEmail": "manager@example.com",
        "isAaCustomer": true,
        "customerStage": "SCALING_UP",
        "maturityScore": 85,
        "currentStatus": "FIRST_VISIT_DONE",
        "createdAt": "2026-03-10T10:00:00Z",
        "updatedAt": "2026-03-15T14:30:00Z",
        "creator": {
          "id": "uuid",
          "name": "王小明"
        },
        "stats": {
          "totalVisits": 1,
          "lastVisitDate": "2026-03-15T10:00:00Z",
          "nextVisitDate": "2026-03-22T14:00:00Z"
        }
      }
    ],
    "pagination": {
      "total": 45,
      "page": 1,
      "limit": 20,
      "totalPages": 3
    }
  }
}
```

### 2. 取得單一客戶詳情
```http
GET /customers/:id
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "companyName": "XX 包租代管公司",
    "contactPerson": "張經理",
    "contactPhone": "0912-345-678",
    "contactEmail": "manager@example.com",
    "website": "https://www.example.com",
    "isAaCustomer": true,
    "customerStage": "SCALING_UP",
    "maturityScore": 85,
    "currentStatus": "FIRST_VISIT_DONE",
    "basicInfo": {
      "hasLineOA": true,
      "companyBackground": "PURE_RENTAL",
      "establishmentStage": "SCALING_UP"
    },
    "visits": [
      {
        "id": "uuid",
        "visitType": "FIRST_VISIT",
        "visitDate": "2026-03-15T10:00:00Z",
        "visitStatus": "COMPLETED"
      }
    ],
    "contracts": [],
    "createdAt": "2026-03-10T10:00:00Z",
    "updatedAt": "2026-03-15T14:30:00Z"
  }
}
```

### 3. 建立客戶
```http
POST /customers
```

**Request Body:**
```json
{
  "companyName": "OO 租賃管理公司",
  "contactPerson": "李經理",
  "contactPhone": "0988-123-456",
  "contactEmail": "contact@example.com",
  "website": "https://www.example.com",
  "customerStage": "NEW_COMPANY"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "companyName": "OO 租賃管理公司",
    "contactPerson": "李經理",
    "isAaCustomer": false,
    "currentStatus": "CONTACTED",
    "createdAt": "2026-03-20T10:30:00Z"
  },
  "message": "客戶建立成功"
}
```

### 4. 更新客戶
```http
PATCH /customers/:id
```

**Request Body:**
```json
{
  "contactPhone": "0988-999-888",
  "customerStage": "SCALING_UP"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "companyName": "OO 租賃管理公司",
    "contactPhone": "0988-999-888",
    "customerStage": "SCALING_UP",
    "updatedAt": "2026-03-20T11:00:00Z"
  },
  "message": "客戶更新成功"
}
```

---

## 拜訪記錄 API

### 1. 建立拜訪記錄
```http
POST /visits
```

**Request Body (一訪):**
```json
{
  "customerId": "uuid",
  "visitType": "FIRST_VISIT",
  "visitDate": "2026-03-20T14:00:00Z",
  "visitStatus": "COMPLETED",
  "basicInfo": {
    "hasWebsite": true,
    "websiteUrl": "https://www.example.com",
    "lineUsage": "LINE_OA",
    "companyStage": "SCALING_UP",
    "companyBackground": ["PURE_RENTAL", "RENOVATION"]
  },
  "propertyStatus": {
    "propertyRatio": {
      "packageRental": 70,
      "propertyManagement": 30
    },
    "propertyTypes": ["SUITE", "WHOLE_FLOOR"],
    "locations": ["台北市", "新北市"],
    "hasSocialHousing": true
  },
  "painPoints": "希望系統化管理可以減少人工對帳時間，目前每月需要3天處理帳務，租客繳款日期不一致造成困擾",
  "notes": "決策者對系統很有興趣，下週安排二訪展示帳務功能",
  "nextAction": "安排二訪，展示帳務自動化功能",
  "nextVisitDate": "2026-03-27T14:00:00Z"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "customerId": "uuid",
    "visitType": "FIRST_VISIT",
    "visitDate": "2026-03-20T14:00:00Z",
    "visitStatus": "COMPLETED",
    "createdAt": "2026-03-20T15:00:00Z"
  },
  "message": "拜訪記錄建立成功"
}
```

### 2. 取得拜訪記錄列表
```http
GET /visits?customerId=uuid&visitType=FIRST_VISIT
```

**Query Parameters:**
- `customerId` (uuid): 篩選特定客戶
- `visitType` (VisitType): 篩選拜訪類型
- `visitStatus` (VisitStatus): 篩選狀態
- `dateFrom` (date): 起始日期
- `dateTo` (date): 結束日期

**Response (200):**
```json
{
  "success": true,
  "data": {
    "visits": [
      {
        "id": "uuid",
        "customerId": "uuid",
        "customer": {
          "companyName": "XX 包租代管公司",
          "isAaCustomer": true
        },
        "visitType": "FIRST_VISIT",
        "visitDate": "2026-03-20T14:00:00Z",
        "visitStatus": "COMPLETED",
        "nextVisitDate": "2026-03-27T14:00:00Z",
        "creator": {
          "name": "王小明"
        }
      }
    ],
    "pagination": {
      "total": 12,
      "page": 1,
      "limit": 20
    }
  }
}
```

### 3. 更新拜訪記錄（二訪資料）
```http
PATCH /visits/:id
```

**Request Body (二訪補充資料):**
```json
{
  "developmentPlan": {
    "planToExpand": true,
    "expansionGoal": "INCREASE_PROPERTIES",
    "hasNewProjects": true,
    "equipmentNeeds": ["SMART_LOCK", "CAMERA"]
  },
  "businessStatus": {
    "organizationData": {
      "totalProperties": 150,
      "totalStaff": 8,
      "accountingStaff": 2
    },
    "accountingMethod": "SYSTEM",
    "hasLandlordReporting": true,
    "totalLandlords": 45,
    "tenantType": "MID_INCOME",
    "hasForeignTenants": true
  },
  "digitalization": {
    "hasAccountingDept": true,
    "accountingDeptSize": 2,
    "currentTools": ["EXCEL", "WORD"],
    "competitorAwareness": ["DDROOM", "包管家"]
  },
  "notes": "客戶對帳務自動化和智能設備整合很感興趣"
}
```

---

## 簽約與導入 API

### 1. 建立簽約記錄
```http
POST /contracts
```

**Request Body:**
```json
{
  "customerId": "uuid",
  "visitId": "uuid",
  "contractDate": "2026-04-01",
  "contractType": "HYBRID",
  "propertyCount": 150,
  "monthlyValue": 450000.00
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "customerId": "uuid",
    "contractDate": "2026-04-01",
    "contractType": "HYBRID",
    "propertyCount": 150,
    "monthlyValue": 450000.00,
    "onboardingSuccess": false,
    "createdAt": "2026-04-01T10:00:00Z"
  },
  "message": "簽約記錄建立成功"
}
```

### 2. 更新導入 KPI
```http
PATCH /contracts/:id/kpis
```

**Request Body:**
```json
{
  "kpiPropertyUploadRate": 65.5,
  "kpiContractCreationRate": 52.0,
  "kpiBillingActive": true,
  "kpiPaymentIntegrated": true,
  "kpiNotificationSetup": false,
  "kpiSopEstablished": true
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "kpiPropertyUploadRate": 65.5,
    "kpiContractCreationRate": 52.0,
    "kpiBillingActive": true,
    "kpiPaymentIntegrated": true,
    "kpiNotificationSetup": false,
    "kpiSopEstablished": true,
    "onboardingSuccess": true,
    "onboardingDate": "2026-04-15T10:00:00Z",
    "updatedAt": "2026-04-15T10:00:00Z"
  },
  "message": "導入 KPI 更新成功"
}
```

---

## 業務績效 API

### 1. 取得個人儀表板
```http
GET /dashboard/personal?period=monthly&date=2026-03
```

**Query Parameters:**
- `period` (daily|weekly|monthly): 統計週期
- `date` (string): 日期（格式依 period 而定）

**Response (200):**
```json
{
  "success": true,
  "data": {
    "period": "monthly",
    "date": "2026-03",
    "metrics": {
      "totalVisits": 28,
      "firstVisits": 12,
      "secondVisits": 8,
      "followUpVisits": 8,
      "contractsSigned": 5,
      "aaCustomersAcquired": 3,
      "conversionRate": 41.67
    },
    "funnel": {
      "contacted": 45,
      "firstVisitDone": 28,
      "secondVisitDone": 15,
      "signed": 5,
      "conversionRates": {
        "contactToFirstVisit": 62.22,
        "firstToSecondVisit": 53.57,
        "secondToSigned": 33.33,
        "overallConversion": 11.11
      }
    },
    "aaCustomers": {
      "total": 23,
      "thisMonth": 3,
      "inProgress": 8
    },
    "upcomingTasks": [
      {
        "customerId": "uuid",
        "companyName": "XX 公司",
        "action": "二訪",
        "scheduledDate": "2026-03-21T14:00:00Z"
      },
      {
        "customerId": "uuid",
        "companyName": "OO 集團",
        "action": "追蹤",
        "scheduledDate": "2026-03-23T10:00:00Z"
      }
    ]
  }
}
```

### 2. 取得團隊績效
```http
GET /dashboard/team?period=monthly&date=2026-03&team=台北團隊
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "period": "monthly",
    "date": "2026-03",
    "team": "台北團隊",
    "teamMetrics": {
      "totalVisits": 156,
      "contractsSigned": 24,
      "aaCustomersAcquired": 15,
      "averageConversionRate": 38.5
    },
    "memberPerformance": [
      {
        "userId": "uuid",
        "userName": "王小明",
        "totalVisits": 28,
        "contractsSigned": 5,
        "conversionRate": 41.67,
        "rank": 1
      },
      {
        "userId": "uuid",
        "userName": "李小華",
        "totalVisits": 32,
        "contractsSigned": 6,
        "conversionRate": 43.75,
        "rank": 1
      }
    ],
    "customerDistribution": {
      "byStage": {
        "INDIVIDUAL": 12,
        "PREPARING_COMPANY": 8,
        "NEW_COMPANY": 15,
        "SCALING_UP": 28
      },
      "byStatus": {
        "CONTACTED": 15,
        "FIRST_VISIT_DONE": 22,
        "SECOND_VISIT_DONE": 12,
        "SIGNED": 14
      }
    }
  }
}
```

---

## 智能分析 API

### 1. 計算客戶成熟度評分
```http
POST /analytics/maturity-score
```

**Request Body:**
```json
{
  "customerId": "uuid",
  "visitData": {
    "propertyCount": 150,
    "staffCount": 8,
    "hasAccountingDept": true,
    "usesManagementSystem": false,
    "planToExpand": true,
    "hasNewProjects": true
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "customerId": "uuid",
    "maturityScore": 85,
    "breakdown": {
      "scale": {
        "score": 28,
        "weight": 0.30,
        "factors": {
          "propertyCount": 150,
          "staffCount": 8
        }
      },
      "digitalization": {
        "score": 18,
        "weight": 0.25,
        "factors": {
          "hasAccountingDept": true,
          "usesManagementSystem": false
        }
      },
      "growthPotential": {
        "score": 23,
        "weight": 0.25,
        "factors": {
          "planToExpand": true,
          "hasNewProjects": true
        }
      },
      "painPointMatch": {
        "score": 16,
        "weight": 0.20,
        "matchedPainPoints": 4
      }
    },
    "recommendation": "高優先級客戶，建議盡快安排二訪並提供完整解決方案"
  }
}
```

### 2. AA 客戶判定
```http
POST /analytics/aa-customer-check
```

**Request Body:**
```json
{
  "customerId": "uuid",
  "visitData": {
    "planToExpand": true,
    "hasLandlordReporting": true,
    "totalProperties": 180,
    "contractType": "PACKAGE_RENTAL",
    "hasForeignTenants": true
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "customerId": "uuid",
    "isAaCustomer": true,
    "matchedCriteria": [
      {
        "id": "criterion-1",
        "name": "規劃擴大營運",
        "matched": true
      },
      {
        "id": "criterion-2",
        "name": "需製作損益表給大房東",
        "matched": true
      },
      {
        "id": "criterion-3",
        "name": "包租100-200戶以上",
        "matched": true
      },
      {
        "id": "criterion-4",
        "name": "有外籍租客",
        "matched": true
      }
    ],
    "recommendation": "AA 客戶，優先排程並提供高階方案"
  }
}
```

---

## 錯誤碼參考

| 錯誤碼 | 說明 |
|--------|------|
| `VALIDATION_ERROR` | 輸入資料驗證失敗 |
| `UNAUTHORIZED` | 未認證或 Token 無效 |
| `FORBIDDEN` | 權限不足 |
| `NOT_FOUND` | 資源不存在 |
| `DUPLICATE_ENTRY` | 重複的資料（如 email 已存在）|
| `INTERNAL_ERROR` | 伺服器內部錯誤 |
| `DATABASE_ERROR` | 資料庫操作失敗 |
| `EXTERNAL_SERVICE_ERROR` | 外部服務呼叫失敗 |

---

## 速率限制

- **一般 API**: 100 requests / 分鐘
- **查詢 API**: 200 requests / 分鐘
- **認證 API**: 10 requests / 分鐘

超過限制時回應：
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "請求次數超過限制，請稍後再試",
    "retryAfter": 60
  }
}
```

---

## Webhook (未來規劃)

系統將支援 Webhook 通知重要事件：

### 事件類型
- `customer.created` - 客戶建立
- `visit.completed` - 拜訪完成
- `contract.signed` - 簽約成功
- `onboarding.completed` - 導入完成

### Webhook Payload 範例
```json
{
  "event": "contract.signed",
  "timestamp": "2026-04-01T10:00:00Z",
  "data": {
    "contractId": "uuid",
    "customerId": "uuid",
    "contractType": "HYBRID",
    "monthlyValue": 450000.00
  }
}
```
