# CAM User Guide Writer - Workflow Diagram

## Overall Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAM User Guide Writer                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Assess Complexity│
                    │ (Low/Med/High)   │
                    └──────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
         ┌──────────┐  ┌──────────┐  ┌──────────┐
         │   Low    │  │  Medium  │  │   High   │
         │ (Manual) │  │ (Capture)│  │(Capture+ │
         │          │  │          │  │  Code)   │
         └──────────┘  └──────────┘  └──────────┘
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                    ┌──────────────────┐
                    │ Gather Materials │
                    │ (A/B/C)          │
                    └──────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
         ┌──────────┐  ┌──────────┐  ┌──────────┐
         │ Option A │  │ Option B │  │ Option C │
         │ Browser  │  │ Multiple │  │ Manual   │
         │ Capture  │  │Materials │  │   Q&A    │
         └──────────┘  └──────────┘  └──────────┘
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                    ┌──────────────────┐
                    │ Search Codebase  │
                    │ (if Med/High)    │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Draft Outline    │
                    │ (Get PM Approval)│
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Write Document   │
                    │ (Follow Rules)   │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ SELF-CHECK       │
                    │ (Mandatory)      │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Deliver to PM    │
                    │ (with placeholders│
                    │  for screenshots)│
                    └──────────────────┘
```

## When to Use What

| Scenario | Complexity | Approach | Tools |
|----------|-----------|----------|-------|
| Simple button/dropdown | Low | Manual Q&A | Option C |
| Multi-step form | Medium | Browser capture | Option A |
| Complex calculations | High | Capture + Code search | Option A + Code |
| Multiple materials available | Any | Synthesize materials | Option B |
| Quick text update | N/A | Don't use skill | Manual edit |

## Information Gathering Methods

### Option A: Live Browser Automation
**When:** UI-heavy features, need screenshots
**Tools:** Playwright, auto_browse_cam.py
**Output:** Screenshots + UI labels + interaction flows

### Option B: Multiple Materials
**When:** PM provides docs/videos/screenshots
**Tools:** Document analysis, video review
**Output:** Synthesized documentation from all sources

### Option C: Manual Q&A
**When:** Low complexity or no materials
**Tools:** Direct conversation with PM
**Output:** Documentation based on PM descriptions

## Code Search Priority (Medium/High Complexity)

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
Draft Outline → PM Approval → Write Document → SELF-CHECK → Deliver
                    ↑                              ↓
                    └──────── Fix Issues ──────────┘
```

## Key Decision Points

### Should I split this into multiple docs?
- **Yes** if: 5+ distinct sub-features, > 2500 words
- **No** if: Single cohesive feature, < 2500 words

### Should I use browser automation?
- **Yes** if: Medium/High complexity, need screenshots
- **No** if: Low complexity, materials already provided

### Should I search codebase?
- **Yes** if: Medium/High complexity, need business rules
- **No** if: Low complexity, UI-only feature
