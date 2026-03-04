# CAM User Guide Writer - Workflow Diagram (v4.0)

## Modular Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│         CAM User Guide Writer (Main Dispatcher)                  │
│         Lightweight orchestrator - delegates to sub-skills       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Step 1: Ask PM Initial Questions       │
        │  - Feature name?                        │
        │  - Materials available?                 │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Step 2: Invoke cam-complexity-assessor │
        │  Returns: Low / Medium / High           │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Step 3: Invoke cam-doc-structure-builder│
        │  Returns: Outline + order number        │
        │  Wait for PM approval                   │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Step 4: Content Gathering              │
        │  (ASK USER FIRST - MANDATORY)           │
        └─────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
    ┌───────────────────┐       ┌───────────────────┐
    │ Ask: Use browser  │       │ Ask: Search       │
    │ automation?       │       │ codebase?         │
    └───────────────────┘       └───────────────────┘
                │                           │
        ┌───────┴───────┐         ┌─────────┴─────────┐
        │               │         │                   │
        ▼               ▼         ▼                   ▼
    ┌─────┐         ┌─────┐   ┌─────┐           ┌─────┐
    │ Yes │         │ No  │   │ Yes │           │ No  │
    └─────┘         └─────┘   └─────┘           └─────┘
        │               │         │                   │
        ▼               │         ▼                   │
┌──────────────┐        │  ┌──────────────┐          │
│ Invoke       │        │  │ Invoke       │          │
│ cam-browser- │        │  │ cam-code-    │          │
│ capture      │        │  │ searcher     │          │
└──────────────┘        │  └──────────────┘          │
        │               │         │                   │
        └───────────────┴─────────┴───────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Step 5: Invoke cam-doc-formatter       │
        │  - Apply formatting rules               │
        │  - Inline validation                    │
        │  Returns: Formatted markdown            │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Step 6: Invoke cam-doc-validator       │
        │  - Comprehensive quality check          │
        │  Returns: Validation report             │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Step 7: Deliver to PM                  │
        │  - Final document                       │
        │  - Validation report                    │
        │  - Next steps                           │
        └─────────────────────────────────────────┘
```

## Sub-Skills Architecture

```
Main Dispatcher (cam-user-guide-writer)
│
├── cam-complexity-assessor
│   └── Asks 3 questions → Returns Low/Medium/High
│
├── cam-doc-structure-builder
│   └── Chooses template → Builds outline → Gets PM approval
│
├── cam-browser-capture (optional - requires user confirmation)
│   └── Playwright automation → Screenshots + UI data
│
├── cam-code-searcher (optional - requires user confirmation)
│   └── Searches i18n/frontend/backend → Extracts business logic
│
├── cam-doc-formatter
│   └── Applies formatting rules → Inline validation
│
└── cam-doc-validator
    └── Comprehensive checks → Validation report
```

## Complexity-Based Workflows

### Low Complexity (Simple UI component)
```
1. Ask initial questions
2. cam-complexity-assessor → Low
3. cam-doc-structure-builder → Outline
4. Manual Q&A with PM (no automation)
5. cam-doc-formatter → Formatted doc
6. cam-doc-validator → Validation report
7. Deliver
```

### Medium Complexity (Multi-step workflow)
```
1. Ask initial questions
2. cam-complexity-assessor → Medium
3. cam-doc-structure-builder → Outline
4. Ask user → cam-browser-capture (if approved)
5. Ask user → cam-code-searcher (optional)
6. cam-doc-formatter → Formatted doc
7. cam-doc-validator → Validation report
8. Deliver
```

### High Complexity (Calculations, backend logic)
```
1. Ask initial questions
2. cam-complexity-assessor → High
3. cam-doc-structure-builder → Outline
4. Ask user → cam-browser-capture (recommended)
5. Ask user → cam-code-searcher (recommended)
6. cam-doc-formatter → Formatted doc
7. cam-doc-validator → Validation report
8. Deliver
```

## When to Use What

| Scenario | Complexity | Browser Capture | Code Search |
|----------|-----------|----------------|-------------|
| Simple button/dropdown | Low | ❌ No | ❌ No |
| Multi-step form | Medium | ✅ Yes (ask user) | ⚠️ Optional |
| Complex calculations | High | ✅ Yes (ask user) | ✅ Yes (ask user) |
| Backend business rules | High | ⚠️ Optional | ✅ Yes (ask user) |
| Quick text update | N/A | ❌ Don't use skill | ❌ Don't use skill |

## Sub-Skill Invocation

All sub-skills are invoked using the Skill tool:

```
Use Skill tool: cam-complexity-assessor
Use Skill tool: cam-doc-structure-builder
Use Skill tool: cam-browser-capture
Use Skill tool: cam-code-searcher
Use Skill tool: cam-doc-formatter
Use Skill tool: cam-doc-validator
```

## User Confirmation Requirements

**IMPORTANT**: The main dispatcher MUST ask the user before invoking:
- `cam-browser-capture` - "Would you like me to use browser automation to capture screenshots?"
- `cam-code-searcher` - "Would you like me to search the codebase for business logic?"

Never invoke these automation sub-skills without explicit user approval.

## Code Search Priority (cam-code-searcher)

```
1. i18n files (HIGHEST PRIORITY)
   ↓ Business rules, warnings, data delays

2. Frontend components
   ↓ UI labels, field options, conditional logic

3. Backend code
   ↓ Calculations, API constraints, data models
```

## Quality Gates

```
Outline → PM Approval → Content Gathering → Formatting → Validation → Deliver
            ↑                                                ↓
            └────────────── Fix Issues ─────────────────────┘
```

## Key Decision Points

### Should I split this into multiple docs?
- **Yes** if: 5+ distinct sub-features, > 2500 words
- **No** if: Single cohesive feature, < 2500 words

### Should I use browser automation?
- **Ask user** for Medium/High complexity
- **Skip** for Low complexity or if materials already provided

### Should I search codebase?
- **Ask user** for Medium/High complexity with business logic
- **Skip** for Low complexity or UI-only features

## Benefits of Modular Architecture

**Before (v3.x)**: 670-line monolithic skill
- All logic in one file
- Hard to maintain
- Mixed concerns

**After (v4.0)**: 134-line dispatcher + 6 focused sub-skills
- Single responsibility per skill
- Easy to maintain and update
- Testable components
- Reusable sub-skills
