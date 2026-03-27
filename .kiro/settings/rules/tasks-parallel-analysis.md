# Task Parallelization Analysis Rules

## Purpose
Identify which implementation tasks can be executed in parallel to optimize development workflow.

## Parallel Execution Criteria

A task can be marked with `(P)` (parallelizable) if it meets ALL of the following:

### 1. No Blocking Dependencies
**The task does not depend on completion of other pending tasks**
- ✅ Parallelizable: Creating independent database models
- ❌ Sequential: Frontend component requiring backend API (must wait for API)

### 2. Independent Implementation Scope
**The task modifies different parts of the codebase**
- ✅ Parallelizable: Implementing two separate services (ExcelService, FileService)
- ❌ Sequential: Multiple tasks modifying the same model/schema (conflicts)

### 3. No Shared State
**The task doesn't rely on shared configuration or setup from other tasks**
- ✅ Parallelizable: Writing unit tests for completed services
- ❌ Sequential: Integration tests requiring database migrations to be applied

### 4. Clear Interface Boundaries
**The task has well-defined inputs/outputs that won't change**
- ✅ Parallelizable: Frontend component with mocked API (interface defined)
- ❌ Sequential: Frontend consuming API still being designed (interface unstable)

## Common Parallelizable Patterns

### Backend Development
- **Multiple independent models** - Different tables with no relationships
- **Separate services** - ExcelService + FileService (no shared code)
- **Independent API endpoints** - Different resources with separate CRUD operations
- **Utility functions** - Helper functions with no dependencies

### Frontend Development
- **Independent UI components** - Separate pages or isolated components
- **Multiple stores** - Pinia stores for different resources
- **Separate API clients** - API clients for different backend resources
- **Static assets** - Icons, styles, translations

### Documentation & Testing
- **Unit tests** - Tests for completed, stable functions
- **Documentation** - User guides, API docs (based on stable interfaces)
- **Data fixtures** - Test data for different models

## Common Sequential Patterns

### Must-Follow Order
1. **Database migrations → Models → CRUD → API → Frontend**
   - Each layer depends on the previous

2. **Schema definition → Implementation → Testing**
   - Cannot test before implementing

3. **API contract → Backend + Frontend**
   - Both sides must agree on interface first

4. **Core service → Service integration → E2E tests**
   - Integration depends on individual services

### Shared Resource Dependencies
- **Database schema changes** - Must be applied before dependent code runs
- **Shared types/interfaces** - Must be defined before usage
- **Authentication/authorization** - Must be implemented before protected endpoints
- **Configuration changes** - Must be deployed before dependent features

## Marking Guidelines

### When to mark `(P)`
- Task has no pending blockers
- Task can start immediately (or after a completed task)
- Multiple developers can work simultaneously
- Integration point clearly defined

### When NOT to mark `(P)`
- Task depends on pending work
- Task modifies shared critical path
- Task requires sequential setup steps
- Interface still under design

## Sequential Mode Override

When `--sequential` flag is used:
- **Do NOT apply any `(P)` markers**
- All tasks executed in strict order
- Ensures conservative, low-risk implementation
- Useful for solo developers or learning projects

## Examples

### Parallelizable (P)
```markdown
## 3. 客戶互動記錄功能

### 3.1 建立 Interaction 資料模型 (P)
建立互動記錄資料表結構

### 3.2 建立 AIAnalysis 資料模型 (P)
建立 AI 分析結果資料表結構

### 3.3 建立 CustomerEvaluation 資料模型 (P)
建立客戶評估資料表結構
```
*These three models are independent and can be created simultaneously*

### Sequential (No Marker)
```markdown
## 2. Excel 名單匯入功能

### 2.1 建立 ImportBatch 資料模型
建立匯入批次追蹤資料表

### 2.2 實作 Excel 解析服務
依賴 2.1 的 ImportBatch model

### 2.3 建立匯入 API 端點
依賴 2.2 的 ExcelService
```
*These tasks must execute in order due to dependencies*

## Validation

Before marking tasks with `(P)`, verify:
- [ ] Task has no dependencies on pending tasks
- [ ] Task modifies independent code sections
- [ ] Task has stable interface/contract
- [ ] Multiple developers could work simultaneously
- [ ] Integration points clearly defined

---
*Focus: Maximize parallelism while ensuring correctness*
