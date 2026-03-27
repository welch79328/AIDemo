# Implementation Tasks Generation Rules

## Core Principles

### 1. Natural Language Focus
**Describe capabilities, not implementation details**
- ✅ Good: "Enable users to upload Excel files containing Facebook ad leads"
- ❌ Bad: "Create ExcelService.parse_facebook_leads() method with pandas.read_excel()"

**Why**: Implementation details belong in design docs. Tasks describe WHAT to build, not HOW.

### 2. Requirement Coverage
**Every requirement must map to at least one task**
- Review requirements.md systematically
- Document requirement IDs in task coverage metadata
- Flag any unmapped requirements as warnings

### 3. Task Sizing
**Target: 1-3 hours per sub-task**
- Break down larger work into manageable pieces
- Each sub-task should be completable in one focused session
- Major tasks can aggregate multiple related sub-tasks

### 4. Progressive Implementation
**Tasks should build incrementally**
- Start with data models and migrations
- Then backend API endpoints
- Then frontend components
- Finally integration and testing

**Dependency awareness**:
- Frontend tasks depend on backend API completion
- Testing tasks depend on feature implementation
- Integration tasks depend on individual components

### 5. Task Structure
**Maximum 2 levels: Major tasks and sub-tasks**
- Major task: "1. Facebook 廣告名單匯入功能"
- Sub-tasks: "1.1 建立資料模型", "1.2 實作 Excel 解析服務", etc.
- No deeper nesting (no 1.1.1, 1.1.2)

**Sequential numbering**:
- Major tasks: 1, 2, 3, 4, ... (never repeat)
- Sub-tasks: 1.1, 1.2, 1.3, ... (reset per major task)

### 6. Collapse Single-Subtask Structures
**Avoid container-only major tasks**
- ❌ Bad: Major task "Set up database" with single subtask "Create migrations"
- ✅ Good: Promote to major task "Create database migrations" OR add more related subtasks

**Container-only major tasks**: When a major task has only implementation via subtasks and no standalone value, minimize duplication:
- Keep major task description minimal (high-level goal only)
- Put detailed requirements, acceptance criteria, and technical notes in subtasks
- Avoid repeating the same information at both levels

### 7. Testing Strategy
**Include testing tasks appropriately**
- Core implementation tasks include basic validation
- Comprehensive test coverage can be separate subtasks
- Mark optional test coverage with `- [ ]*` when:
  - Acceptance criteria already satisfied by core implementation
  - Can be deferred post-MVP without risk
  - Represents nice-to-have quality improvements

**Test Coverage Principles**:
- Unit tests for services and utilities
- Integration tests for API endpoints
- E2E tests for critical user flows
- Deferred: Edge cases, performance tests, visual regression

### 8. Integration Tasks
**Every task must connect to the system**
- No orphaned work that doesn't integrate
- Include "wire-up" subtasks where needed
- Test integration, not just individual components

## Task Metadata

### Requirements Coverage
**Format**: Numeric IDs only, comma-separated
- ✅ Good: `覆蓋需求: 1.1, 1.2, 1.3`
- ❌ Bad: `覆蓋需求: 1.1 (匯入功能), 1.2 (資料驗證), 1.3 (批次追蹤)`

**Why**: Keep coverage metadata concise. Descriptions belong in requirement sections.

### Parallel Markers
**Use `(P)` markers for parallelizable tasks**
- Applied based on tasks-parallel-analysis.md criteria
- Only in non-sequential mode
- Indicates tasks with no blocking dependencies

### Status Indicators
**Standard checkboxes**:
- `- [ ]`: Pending task
- `- [x]`: Completed task
- `- [ ]*`: Optional/deferred task (e.g., comprehensive test coverage)

## Task Template Structure

```markdown
## X. Major Task Name

Brief description of the major task goal.

**覆蓋需求**: X.X, X.X, X.X

### X.1 Sub-task Name

**目標**: What this subtask accomplishes

**接受標準**:
- Specific, testable criterion 1
- Specific, testable criterion 2

**技術要點**:
- Key technical consideration 1
- Key technical consideration 2

**預估時間**: X hours
```

## Quality Checklist

Before finalizing tasks.md, verify:
- [ ] All requirements mapped to tasks
- [ ] Task dependencies are logical
- [ ] Each sub-task is 1-3 hours
- [ ] No orphaned work (all tasks integrate)
- [ ] Testing tasks included appropriately
- [ ] Natural language (capabilities, not code)
- [ ] Maximum 2 levels (major + sub)
- [ ] Sequential numbering correct
- [ ] Parallel markers applied (if applicable)
- [ ] Single-subtask structures collapsed
- [ ] Container-only major tasks minimized

## Common Patterns

### Database & Models
1. Define data models (SQLAlchemy/Pydantic)
2. Create migrations
3. Test model relationships and constraints

### Backend API
1. Create schemas (request/response)
2. Implement CRUD operations
3. Create API endpoints
4. Add error handling
5. Test endpoints

### Frontend Feature
1. Create API client functions
2. Define TypeScript interfaces
3. Implement UI components
4. Connect to state management
5. Add routing
6. Test user flows

### Service Integration
1. Create service class
2. Implement core logic
3. Add error handling & retry
4. Write unit tests
5. Integrate with API layer

## Language & Localization

- Use language specified in spec.json (e.g., zh-TW)
- Task names, descriptions, and acceptance criteria in target language
- Technical terms can remain in English (e.g., "SQLAlchemy", "Pydantic")
- Code examples and file paths in English

---
*Focus: Capability descriptions, requirement coverage, progressive implementation*
