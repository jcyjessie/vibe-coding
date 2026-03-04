# CAM User Guide Writer - Skill Modularization Design

**Date:** 2026-03-04
**Status:** Approved
**Version:** 4.0.0

## Executive Summary

Restructure the monolithic cam-user-guide-writer skill (670 lines, 39MB) into a lean, modular architecture with 6 focused sub-skills. This implements all 6 optimizations: split monolithic skill, move reference content, externalize captured data, simplify conditional logic, remove archive content, and consolidate checklists.

**Impact:**
- Main skill: 670 lines → 100 lines (85% reduction)
- Total size: 39MB → 20MB (48% reduction)
- Architecture: Monolithic → Modular (7 independent skills)
- Maintainability: Single responsibility per skill

## Design Decisions

### Decision 1: Hybrid Dispatcher Pattern
**Chosen:** Main skill acts as lightweight dispatcher that asks questions, then explicitly invokes sub-skills using Skill tool.

**Rationale:** Provides control over flow while keeping sub-skills modular and independently testable.

### Decision 2: Delete Captured Data & Archive
**Chosen:** Delete all test artifacts (19MB captured_data/, 192KB archive/).

**Rationale:** Skills should contain logic, not data. Screenshots are captured fresh during actual doc writing and saved to cam-docs repo. Archive contains old code versions preserved in git history.

### Decision 3: Embed References in Sub-Skills
**Chosen:** Move formatting-guide.md into cam-doc-formatter, browser-automation.md into cam-browser-capture, code-search.md into cam-code-searcher.

**Rationale:** Each sub-skill becomes self-contained with its own rules. Easier to maintain and test.

### Decision 4: Two-Phase Validation
**Chosen:** Inline checks during writing + comprehensive final validation sub-skill.

**Rationale:** Catch obvious errors early (missing frontmatter, Chinese characters) while writing, then run thorough quality checks at end. Fast feedback + comprehensive review.

### Decision 5: Scripts in Browser Capture Sub-Skill
**Chosen:** Move all 8 Python scripts to cam-browser-capture/scripts/.

**Rationale:** Browser automation scripts belong with the browser capture sub-skill. Keeps dependencies clear and makes sub-skill self-contained.

### Decision 6: Granular Split (6 Sub-Skills)
**Chosen:** Maximum modularity with single responsibility per skill.

**Rationale:** Each skill has one clear purpose. Easier to maintain, test, and extend. Can be used independently or composed.

## Architecture

### Overall Structure

```
cam-user-guide-writer (main dispatcher, 100 lines)
├── cam-complexity-assessor (80 lines)
├── cam-doc-structure-builder (120 lines)
├── cam-doc-formatter (150 lines)
├── cam-browser-capture (100 lines + scripts/)
├── cam-code-searcher (130 lines)
└── cam-doc-validator (180 lines)
```

### Invocation Flow

```
User → Main Dispatcher
  ↓
  → cam-complexity-assessor (returns: Low/Medium/High)
  ↓
  → cam-doc-structure-builder (returns: outline)
  ↓
  → Content gathering (ASK USER FIRST):
     - Low: Manual Q&A only (no sub-skills)
     - Medium: Ask user about browser capture + optional code search
     - High: Recommend both browser capture AND code search, get confirmation
  ↓
  → cam-doc-formatter (writes content with inline checks)
  ↓
  → cam-doc-validator (final quality check)
```

**Key principle:** Dispatcher makes recommendations but ALWAYS gets explicit user confirmation before invoking automation sub-skills (cam-browser-capture or cam-code-searcher).

## Sub-Skill Specifications

### 1. cam-complexity-assessor (~80 lines)
**Purpose:** Determine feature complexity level

**Inputs:** Feature name, PM description
**Outputs:** Low/Medium/High complexity rating

**Logic:**
- Asks PM 3 questions:
  1. "Does this feature involve calculations or backend logic?" (Yes → High)
  2. "Does it have multiple workflows or configuration options?" (Yes → Medium)
  3. "Is it a simple UI component?" (Yes → Low)
- Returns complexity level to dispatcher

**Dependencies:** None

### 2. cam-doc-structure-builder (~120 lines)
**Purpose:** Choose document template and build outline

**Inputs:** Complexity level, feature type
**Outputs:** Document outline with sections

**Logic:**
- Checks existing docs for similar structure
- Determines file order number
- Chooses template: Setup Guide / Feature Manual / FAQ
- Builds section outline
- Asks PM for approval before proceeding

**Dependencies:** Reads `/Users/jessiecao/src/cam-docs/docs/user-guide/` for context

### 3. cam-doc-formatter (~150 lines)
**Purpose:** Write content with formatting rules + inline validation

**Inputs:** Outline, gathered content (from Q&A/browser/code)
**Outputs:** Formatted markdown document

**Embedded content:**
- Formatting rules (from current `references/formatting-guide.md`)
- CAM terminology glossary
- Inline validation checks:
  - ✓ No Chinese characters
  - ✓ UI elements bolded
  - ✓ Bullet lists use `-`
  - ✓ Navigation format correct

**Dependencies:** None (self-contained)

### 4. cam-browser-capture (~100 lines + scripts/)
**Purpose:** Automate screenshot capture via browser automation

**Inputs:** CAM URL, feature name
**Outputs:** Screenshots + UI element data (JSON)

**Embedded content:**
- Browser automation guide (from current `references/browser-automation.md`)
- Python scripts directory:
  - `auto_browse_cam_v3.py`
  - `explore_field_dependencies.py`
  - `browse_cam.py`
  - `auto_login_cam_v3.py`
  - `cam_doc.py`
  - `retry_handler.py`
  - `selector_engine.py`
  - `state_tracker.py`
  - `.auth/` (preserved)

**Dependencies:** Playwright, Chrome with debug port

### 5. cam-code-searcher (~130 lines)
**Purpose:** Search CAM codebase for business logic

**Inputs:** Feature name, search scope (i18n/frontend/backend)
**Outputs:** Extracted business rules, formulas, validation logic

**Embedded content:**
- Code search patterns (from current `references/code-search.md`)
- Search priority order:
  1. i18n files (business explanations)
  2. Frontend components (field options)
  3. Backend code (calculations)

**Dependencies:** Access to `/Users/jessiecao/src/cam/` codebase

### 6. cam-doc-validator (~180 lines)
**Purpose:** Comprehensive final quality check

**Inputs:** Completed markdown document
**Outputs:** Validation report with pass/fail + fixes

**Validation categories:**
- Frontmatter (7 checks)
- Structure (3 checks)
- Content completeness (5 checks)
- Language & formatting (4 checks)
- Screenshot coverage (3 checks)

**Consolidated from 3 current checklists** (lines 125-153, 564-597, 628-670)

**Dependencies:** None (self-contained)

## Content Gathering Strategy

### Low Complexity Flow
**Criteria:** Simple UI component, single interaction, no calculations

**Dispatcher behavior:**
1. Assess as Low complexity
2. Tell user: "This is a simple feature. I'll gather information through Q&A."
3. Proceed with manual questions (no sub-skill invocation)

### Medium Complexity Flow
**Criteria:** Multiple interactions, configuration options, UI-heavy, minimal backend logic

**Dispatcher behavior:**
1. Assess as Medium complexity
2. **Ask user:** "I recommend using browser capture for screenshots. Would you like me to run the automation script?"
   - If yes → Invoke `cam-browser-capture`
   - If no → Manual Q&A
3. **Ask user:** "Should I search the codebase for field options and validation rules?"
   - If yes → Invoke `cam-code-searcher`
   - If no → Skip

### High Complexity Flow
**Criteria:** Calculations, formulas, backend logic, business rules, data delays

**Dispatcher behavior:**
1. Assess as High complexity
2. **Ask user:** "This feature has complex logic. I recommend:
   - Browser capture for UI screenshots
   - Code search for business logic and formulas

   Would you like me to run both automation tools?"
   - If yes to both → Invoke both in parallel
   - If yes to one → Invoke that one only
   - If no to both → Manual Q&A

## Data Migration & Cleanup

### Current State
- 39MB total skill directory
- 19MB in `scripts/captured_data/` (141 PNG files)
- 192KB in `archive/` (old script versions)
- 20KB in `references/` (3 markdown files)

### Migration Plan

#### Delete captured_data/ (Optimization #3)
```bash
rm -rf /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/captured_data/
rm -rf /Users/jessiecao/.claude/skills/cam-user-guide-writer/captured_data/
```
**Rationale:** Test artifacts from development. Fresh screenshots saved to `/Users/jessiecao/src/cam-docs/docs/user-guide/resources/<feature-name>/`

**Impact:** -19MB (49% reduction)

#### Delete archive/ (Optimization #5)
```bash
rm -rf /Users/jessiecao/.claude/skills/cam-user-guide-writer/archive/
```
**Rationale:** Old script versions preserved in git history

**Impact:** -192KB

#### Embed references/ into sub-skills (Optimization #2)
```bash
rm -rf /Users/jessiecao/.claude/skills/cam-user-guide-writer/references/
```

**Migration mapping:**
- `references/formatting-guide.md` → Embed in `cam-doc-formatter/skill.md`
- `references/browser-automation.md` → Embed in `cam-browser-capture/skill.md`
- `references/code-search.md` → Embed in `cam-code-searcher/skill.md`

**Impact:** -20KB (content preserved in sub-skills)

### Final Size Estimate
- Before: 39MB
- After: ~20MB (48% reduction)
- Main skill: ~100 lines (from 670 lines, 85% reduction)

## New File Structure

### Before (Monolithic)
```
cam-user-guide-writer/
├── skill.md (670 lines)
├── README.md
├── CHANGELOG.md
├── references/
│   ├── formatting-guide.md
│   ├── browser-automation.md
│   └── code-search.md
├── scripts/
│   ├── *.py (8 files)
│   └── captured_data/ (19MB)
├── archive/ (192KB)
├── evals/
└── docs/
```

### After (Modular)
```
cam-user-guide-writer/
├── skill.md (100 lines - main dispatcher)
├── README.md (updated with new structure)
├── CHANGELOG.md (add v4.0.0 entry)
├── evals/
└── docs/

cam-complexity-assessor/
├── skill.md (80 lines)
└── README.md

cam-doc-structure-builder/
├── skill.md (120 lines)
└── README.md

cam-doc-formatter/
├── skill.md (150 lines - includes formatting rules)
└── README.md

cam-browser-capture/
├── skill.md (100 lines - includes automation guide)
├── README.md
└── scripts/
    ├── auto_browse_cam_v3.py
    ├── explore_field_dependencies.py
    ├── browse_cam.py
    ├── auto_login_cam_v3.py
    ├── cam_doc.py
    ├── retry_handler.py
    ├── selector_engine.py
    ├── state_tracker.py
    └── .auth/ (preserved)

cam-code-searcher/
├── skill.md (130 lines - includes search patterns)
└── README.md

cam-doc-validator/
├── skill.md (180 lines - consolidated checklists)
└── README.md
```

**Key changes:**
- 7 separate skill directories (1 main + 6 sub-skills)
- Each sub-skill is self-contained with its own README
- Python scripts moved to cam-browser-capture only
- No references/, archive/, or captured_data/ directories
- Total: ~760 lines across 7 skills (vs 670 in one file)
- Each skill is focused and independently testable

## Migration Strategy

**Approach:** Clean slate migration (not in-place refactoring)

### Phase 1: Create New Sub-Skill Directories
```bash
# Create 6 new skill directories alongside cam-user-guide-writer
/Users/jessiecao/.claude/skills/
├── cam-user-guide-writer/ (existing, will be refactored)
├── cam-complexity-assessor/ (new)
├── cam-doc-structure-builder/ (new)
├── cam-doc-formatter/ (new)
├── cam-browser-capture/ (new)
├── cam-code-searcher/ (new)
└── cam-doc-validator/ (new)
```

### Phase 2: Extract Content to Sub-Skills
**For each sub-skill:**
1. Create `skill.md` with focused content extracted from main skill
2. Create `README.md` with usage instructions
3. Add skill metadata (name, description, trigger conditions)

**Content extraction mapping:**
- Lines 312-391 (Step 0: Assess Complexity) → `cam-complexity-assessor/skill.md`
- Lines 492-541 (Step 3-4: Structure) → `cam-doc-structure-builder/skill.md`
- Lines 1-290 (Formatting rules) → `cam-doc-formatter/skill.md`
- `references/browser-automation.md` + scripts/ → `cam-browser-capture/`
- `references/code-search.md` + lines 415-441 → `cam-code-searcher/skill.md`
- Lines 125-153, 564-597, 628-670 (checklists) → `cam-doc-validator/skill.md`

### Phase 3: Refactor Main Skill as Dispatcher
1. Reduce `cam-user-guide-writer/skill.md` to ~100 lines
2. Remove all business logic
3. Add sub-skill invocation logic using Skill tool
4. Update description to mention it's a dispatcher

### Phase 4: Clean Up Old Content
```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer
rm -rf scripts/captured_data/
rm -rf captured_data/
rm -rf archive/
rm -rf references/
```

### Phase 5: Move Python Scripts
```bash
# Move scripts to cam-browser-capture
mv /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/*.py \
   /Users/jessiecao/.claude/skills/cam-browser-capture/scripts/

# Move .auth directory
mv /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/.auth \
   /Users/jessiecao/.claude/skills/cam-browser-capture/scripts/
```

### Phase 6: Update Documentation
- Update main README.md with new architecture
- Add CHANGELOG.md entry for v4.0.0
- Create README.md for each sub-skill

### Phase 7: Testing
- Test main dispatcher invocation flow
- Test each sub-skill independently
- Verify Python scripts work in new location
- Run existing evals to ensure no regression

**Rollback plan:** Keep original cam-user-guide-writer in git history. If issues arise, can revert to v3.1.0.

## Success Criteria

1. **Size reduction:** Skill directory reduced from 39MB to ~20MB
2. **Code reduction:** Main skill reduced from 670 lines to ~100 lines
3. **Modularity:** Each sub-skill can be invoked independently
4. **Maintainability:** Single responsibility per skill
5. **No regression:** All existing evals pass
6. **User experience:** Dispatcher asks for confirmation before automation

## Implementation Notes

- Use Skill tool for sub-skill invocation (not direct file reads)
- Preserve .auth/ directory for browser automation
- Update skill descriptions for better triggering
- Add comprehensive README to each sub-skill
- Version as 4.0.0 (breaking change from monolithic to modular)

## Risks & Mitigations

**Risk 1:** Sub-skill invocation overhead
**Mitigation:** Dispatcher is lightweight, minimal overhead

**Risk 2:** Breaking existing workflows
**Mitigation:** Keep v3.1.0 in git history, comprehensive testing before release

**Risk 3:** Python scripts fail in new location
**Mitigation:** Test all scripts after migration, update paths if needed

**Risk 4:** Users confused by new structure
**Mitigation:** Update README with clear architecture diagram and usage examples
