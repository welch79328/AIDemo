# Gap Analysis Framework

## Purpose
Analyze implementation gap between approved requirements and existing codebase to inform design decisions.

## Analysis Approach

### 1. Codebase Investigation

#### Backend Analysis
- **Framework & Structure**: Identify framework (FastAPI, Django, Flask), routing patterns, middleware
- **Data Layer**: Examine ORM models, database schema, migration patterns
- **API Patterns**: Review endpoint conventions, request/response formats, validation approaches
- **Service Layer**: Identify business logic organization, service classes, helper utilities
- **File Handling**: Check existing file upload/storage mechanisms
- **External Integrations**: Review patterns for third-party API integration
- **Authentication & Authorization**: Examine user management, permission systems

#### Frontend Analysis
- **Framework & Structure**: Identify Vue version, component architecture, state management
- **Routing**: Review routing patterns, route guards, navigation
- **API Client**: Examine API communication patterns, HTTP client setup
- **UI Components**: Identify component library, reusable components
- **State Management**: Check Vuex/Pinia usage, store modules
- **File Upload UI**: Review existing file upload components
- **Form Patterns**: Examine validation, error handling, submission flows

#### Database Analysis
- **Schema**: Review existing tables, relationships, indexes
- **Conventions**: Identify naming patterns, timestamp fields, soft deletes
- **Migrations**: Check migration tool and patterns

### 2. Requirement Mapping

For each major requirement area, identify:

1. **Fully Covered**: Existing functionality that meets requirement
2. **Partially Covered**: Existing functionality needing extension/modification
3. **Not Covered**: New functionality required
4. **Reusable Components**: Existing code/patterns that can be leveraged

### 3. Integration Analysis

Evaluate how new features integrate with existing:
- Data models and relationships
- API endpoints and routing
- Frontend components and pages
- Authentication and permissions
- File storage and management
- External service integrations

### 4. Implementation Approaches

For each major gap, evaluate:

#### Option A: Extend Existing
- **Pros**: Maintains consistency, reuses existing patterns
- **Cons**: May introduce complexity, coupling
- **When**: Existing code is well-structured and closely related

#### Option B: Build New
- **Pros**: Clean separation, independent development
- **Cons**: Potential duplication, integration overhead
- **When**: Requirements diverge significantly from existing patterns

#### Option C: Hybrid
- **Pros**: Balances reuse and clean design
- **Cons**: Requires careful planning
- **When**: Some components align, others don't

### 5. Risk & Dependency Assessment

Identify:
- **Technical Risks**: Complex integrations, performance concerns, unknown technologies
- **Dependencies**: External services, data sources, third-party libraries
- **Research Needs**: Areas requiring proof-of-concept or further investigation
- **Migration Concerns**: Data migration, backward compatibility

## Output Structure

### Executive Summary
- **Scope**: One-sentence project scope
- **Existing Foundation**: Brief assessment of current codebase (2-3 sentences)
- **Implementation Complexity**: High/Medium/Low with justification
- **Key Challenges**: Top 3-5 technical challenges
- **Recommended Approach**: High-level strategy (extend/new/hybrid)

### Detailed Findings

#### 1. Codebase Assessment

##### Backend
- Framework: [Name and version]
- Key patterns: [Bullet list]
- Strengths: [What works well]
- Limitations: [What may need work]

##### Frontend
- Framework: [Name and version]
- Key patterns: [Bullet list]
- Strengths: [What works well]
- Limitations: [What may need work]

##### Database
- Database: [Type and version]
- Schema patterns: [Bullet list]
- Migration tool: [Tool name]

#### 2. Requirement Gap Analysis

For each major requirement area:

##### [Requirement Name]
- **Status**: ✅ Fully Covered / ⚠️ Partially Covered / ❌ Not Covered
- **Existing Components**: [List relevant existing code]
- **Required Changes**: [What needs to be added/modified]
- **Reusable Patterns**: [Existing patterns to leverage]
- **Implementation Approach**: [Extend/New/Hybrid]
- **Complexity**: [High/Medium/Low]

#### 3. Integration Points

- **Data Model Integration**: [How new models relate to existing]
- **API Integration**: [How new endpoints fit into existing routing]
- **Frontend Integration**: [How new pages/components integrate]
- **Authentication Integration**: [How permissions apply]
- **File Storage Integration**: [How file handling works]

#### 4. External Dependencies

List each external service/library needed:
- **Service Name**: [e.g., AI Speech-to-Text]
  - Purpose: [Why needed]
  - Options: [Potential providers]
  - Integration Complexity: [High/Medium/Low]
  - Cost Considerations: [If applicable]

#### 5. Technical Risks

- **Risk 1**: [Description]
  - Impact: [High/Medium/Low]
  - Mitigation: [How to address]

- **Risk 2**: [Description]
  - Impact: [High/Medium/Low]
  - Mitigation: [How to address]

#### 6. Research & Investigation Needs

Areas requiring further research before design:
- **[Topic]**: [Why research needed, what to investigate]

#### 7. Recommended Implementation Strategy

- **Overall Approach**: [Extend/New/Hybrid with rationale]
- **Phase 1 Priorities**: [What to build first]
- **Integration Strategy**: [How to integrate with existing system]
- **Testing Strategy**: [How to ensure quality]
- **Migration Considerations**: [If applicable]

### Appendices

#### Data Model Changes
- New tables: [List]
- Modified tables: [List]
- New relationships: [List]

#### API Endpoint Changes
- New endpoints: [List]
- Modified endpoints: [List]

#### Frontend Page Changes
- New pages: [List]
- Modified pages: [List]

## Investigation Tools

- **Glob**: Find files by pattern (models, views, components, etc.)
- **Grep**: Search code for patterns, function names, imports
- **Read**: Examine key files in detail
- **WebSearch/WebFetch**: Research external dependencies, best practices

## Best Practices

1. **Be Thorough**: Search broadly before concluding something doesn't exist
2. **Multiple Options**: Present alternatives when applicable
3. **Flag Unknowns**: Explicitly note areas needing research
4. **Concrete Evidence**: Reference actual file paths and code patterns
5. **Practical Focus**: Emphasize actionable insights for design phase
