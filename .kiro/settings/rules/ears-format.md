# EARS Format Guidelines

## Overview
EARS (Easy Approach to Requirements Syntax) provides structured patterns for writing clear, testable requirements.

## EARS Patterns

### 1. Ubiquitous (General)
**Format**: `The <system> shall <requirement>`

**Example**:
- The system shall encrypt all user passwords using bcrypt
- The API shall return responses in JSON format

**Usage**: For requirements that always apply

### 2. Event-Driven
**Format**: `WHEN <trigger>, the <system> shall <requirement>`

**Example**:
- WHEN a user submits a form, the system shall validate all required fields
- WHEN a file upload exceeds 10MB, the system shall reject the upload

**Usage**: For requirements triggered by specific events

### 3. State-Driven
**Format**: `WHILE <state>, the <system> shall <requirement>`

**Example**:
- WHILE a user is authenticated, the system shall display the dashboard
- WHILE processing a payment, the system shall disable the submit button

**Usage**: For requirements active during specific states

### 4. Unwanted Behavior
**Format**: `IF <condition>, THEN the <system> shall <requirement>`

**Example**:
- IF login fails 3 times, THEN the system shall lock the account for 15 minutes
- IF a database connection fails, THEN the system shall retry up to 3 times

**Usage**: For error handling and edge cases

### 5. Optional Features
**Format**: `WHERE <feature enabled>, the <system> shall <requirement>`

**Example**:
- WHERE two-factor authentication is enabled, the system shall require OTP verification
- WHERE admin mode is active, the system shall display additional debugging information

**Usage**: For conditional features

## Best Practices

1. **Be Specific**: Use concrete, measurable criteria
   - ✅ "The system shall respond within 200ms"
   - ❌ "The system shall be fast"

2. **Use Active Voice**: Focus on what the system does
   - ✅ "The system shall validate email format"
   - ❌ "Email format should be validated"

3. **One Requirement Per Statement**: Avoid compound requirements
   - ✅ Split into two: "The system shall validate input" + "The system shall sanitize input"
   - ❌ "The system shall validate and sanitize input"

4. **Choose Appropriate Subject**:
   - For software: Use system/service name (e.g., "The API shall...", "The dashboard shall...")
   - For hardware: Use component name
   - Be consistent throughout the document

5. **Testable Criteria**: Each requirement must be verifiable
   - ✅ "The system shall support up to 1000 concurrent users"
   - ❌ "The system shall support many users"

## Language Localization

When writing in languages other than English (e.g., Traditional Chinese), maintain EARS structure:

**Chinese Example**:
- 當使用者提交表單時，系統應驗證所有必填欄位
- 在使用者已認證的狀態下，系統應顯示儀表板
- 系統應在 200 毫秒內回應請求

Keep trigger words (WHEN/當, WHILE/在...狀態下, IF...THEN/如果...則, WHERE/在...情況下) clearly identifiable.
