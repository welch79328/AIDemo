# Steering Principles

## Purpose
Steering files capture project patterns and principles to guide AI development decisions.

## Golden Rule
**If new code follows existing patterns, steering shouldn't need updating.**

Document patterns and principles, not exhaustive lists.

## Granularity Guidelines

### Good Examples (Patterns)
- "Feature-first directory structure: `/features/{feature-name}/{type}`"
- "API endpoints follow RESTful conventions with versioning: `/api/v1/{resource}`"
- "TypeScript strict mode enabled, prefer interfaces over types for public APIs"
- "Services use dependency injection pattern with constructor parameters"

### Bad Examples (Lists)
- Listing every file in the codebase
- Enumerating all npm dependencies
- Cataloging every component or function
- Complete directory tree dumps

## Security
**Never include**:
- API keys, tokens, passwords
- Database credentials
- Secret configuration values
- Private endpoints or internal URLs

## Content Guidelines

### product.md
- **Purpose**: What problem does this solve? Who uses it?
- **Value Proposition**: Core benefits and capabilities
- **User Experience**: Key workflows and interactions
- **Domain Concepts**: Business terminology and rules

### tech.md
- **Stack**: Framework versions and key libraries (pattern, not full package list)
- **Architectural Decisions**: Why certain technologies were chosen
- **Conventions**: Coding standards, naming patterns
- **Integration Patterns**: How external services are integrated

### structure.md
- **Organization Pattern**: How code is organized (e.g., feature-first, layered)
- **Module Boundaries**: Separation of concerns
- **Import Conventions**: How modules reference each other
- **File Naming**: Patterns and examples

## Custom Steering Files
- Users can add domain-specific files (e.g., `api-standards.md`, `testing.md`)
- All `.kiro/steering/*.md` are treated equally
- Custom files follow same granularity principles

## Update Philosophy
- **Additive**: Add new patterns, don't replace existing content
- **Preserve**: User customizations are sacred
- **Detect Drift**: Code not following patterns → Warning
- **Suggest Extensions**: New patterns emerging → Update candidate

## Exclusions
Do not document:
- Agent-specific directories (`.cursor/`, `.gemini/`, `.claude/`)
- `.kiro/settings/` content (this is metadata, not project knowledge)
- Detailed `.kiro/specs/` content (light references OK)
- Build artifacts, logs, temporary files
