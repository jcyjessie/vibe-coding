# Skill Modularization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restructure monolithic cam-user-guide-writer skill (670 lines, 39MB) into 6 focused sub-skills with hybrid dispatcher pattern.

**Architecture:** Clean slate migration - create 6 new skill directories, extract content from monolithic skill.md, move Python scripts to cam-browser-capture, delete test artifacts (19MB), refactor main skill as lightweight dispatcher.

**Tech Stack:** Markdown (skill definitions), Python (browser automation scripts), Git (version control)

---

## Task 1: Create Sub-Skill Directories

Create 6 new skill directories alongside cam-user-guide-writer.

```bash
cd /Users/jessiecao/.claude/skills
mkdir -p cam-complexity-assessor
mkdir -p cam-doc-structure-builder
mkdir -p cam-doc-formatter
mkdir -p cam-browser-capture/scripts
mkdir -p cam-code-searcher
mkdir -p cam-doc-validator
```

Verify: `ls -la | grep cam-` should show 7 directories

Commit:
```bash
git add cam-*
git commit -m "chore: create sub-skill directory structure for modular architecture"
```

---

## Task 2: Create cam-complexity-assessor Sub-Skill

Extract complexity assessment logic (lines 312-391 from main skill) into focused sub-skill.

**Create skill.md:**
- Frontmatter with name/description
- 3-question assessment process (backend logic → workflows → UI simplicity)
- Complexity criteria (High/Medium/Low)
- Output format

**Create README.md:**
- Purpose: Assess feature complexity
- Usage: Invoked by main dispatcher
- Returns: Low/Medium/High complexity rating

Commit:
```bash
cd cam-complexity-assessor
git add skill.md README.md
git commit -m "feat(cam-complexity-assessor): add complexity assessment sub-skill"
```

---

## Task 3: Create cam-doc-structure-builder Sub-Skill

Extract structure building logic (lines 492-541 from main skill) into focused sub-skill.

**Create skill.md:**
- Check existing docs for context
- Determine file order number
- Choose template (Setup Guide / Feature Manual / FAQ)
- Build section outline
- Ask PM for approval

**Create README.md:**
- Purpose: Choose document template and build outline
- Dependencies: Reads `/Users/jessiecao/src/cam-docs/docs/user-guide/`
- Returns: Document outline with sections

Commit:
```bash
cd cam-doc-structure-builder
git add skill.md README.md
git commit -m "feat(cam-doc-structure-builder): add structure building sub-skill"
```

---

## Task 4: Create cam-doc-formatter Sub-Skill

Extract formatting rules (lines 1-290 from main skill) and embed `references/formatting-guide.md`.

**Create skill.md:**
- Embed formatting rules from `references/formatting-guide.md`
- CAM terminology glossary
- Inline validation checks (no Chinese, UI bolded, bullets use `-`, navigation format)
- Write content with formatting applied

**Create README.md:**
- Purpose: Write content with formatting rules + inline validation
- Self-contained: No external dependencies
- Inline checks: Catch obvious errors early

Commit:
```bash
cd cam-doc-formatter
git add skill.md README.md
git commit -m "feat(cam-doc-formatter): add formatting sub-skill with embedded rules"
```

---

## Task 5: Create cam-browser-capture Sub-Skill

Embed `references/browser-automation.md` and prepare for Python scripts migration.

**Create skill.md:**
- Embed browser automation guide from `references/browser-automation.md`
- Document automatic vs interactive modes
- Prerequisites (Playwright, Chrome debug port)
- Script usage instructions

**Create README.md:**
- Purpose: Automate screenshot capture via browser automation
- Dependencies: Playwright, Chrome with debug port
- Scripts: Will contain 8 Python files + .auth/

Commit:
```bash
cd cam-browser-capture
git add skill.md README.md
git commit -m "feat(cam-browser-capture): add browser capture sub-skill with embedded guide"
```

---

## Task 6: Create cam-code-searcher Sub-Skill

Extract code search logic (lines 415-441 from main skill) and embed `references/code-search.md`.

**Create skill.md:**
- Embed code search patterns from `references/code-search.md`
- Search priority order (i18n → frontend → backend)
- Grep patterns and search techniques
- Extract business rules, formulas, validation logic

**Create README.md:**
- Purpose: Search CAM codebase for business logic
- Dependencies: Access to `/Users/jessiecao/src/cam/` codebase
- Returns: Extracted business rules, formulas, validation logic

Commit:
```bash
cd cam-code-searcher
git add skill.md README.md
git commit -m "feat(cam-code-searcher): add code search sub-skill with embedded patterns"
```

---

## Task 7: Create cam-doc-validator Sub-Skill

Consolidate 3 validation checklists (lines 125-153, 564-597, 628-670 from main skill).

**Create skill.md:**
- Frontmatter validation (7 checks)
- Structure validation (3 checks)
- Content completeness (5 checks)
- Language & formatting (4 checks)
- Screenshot coverage (3 checks)
- Two-phase validation approach

**Create README.md:**
- Purpose: Comprehensive final quality check
- Self-contained: No external dependencies
- Returns: Validation report with pass/fail + fixes

Commit:
```bash
cd cam-doc-validator
git add skill.md README.md
git commit -m "feat(cam-doc-validator): add validation sub-skill with consolidated checklists"
```

---

## Task 8: Move Python Scripts to cam-browser-capture

Move all 8 Python scripts and .auth/ directory to cam-browser-capture/scripts/.

```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer
mv scripts/*.py ../cam-browser-capture/scripts/
mv scripts/.auth ../cam-browser-capture/scripts/
```

Verify scripts work in new location:
```bash
cd /Users/jessiecao/.claude/skills/cam-browser-capture/scripts
python auto_browse_cam_v3.py --help
```

Commit:
```bash
cd /Users/jessiecao/.claude/skills
git add cam-browser-capture/scripts/
git add cam-user-guide-writer/scripts/
git commit -m "refactor: move Python scripts to cam-browser-capture sub-skill"
```

---

## Task 9: Delete Test Artifacts and Archive

Delete captured_data/ (19MB) and archive/ (192KB) directories.

```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer
rm -rf scripts/captured_data/
rm -rf captured_data/
rm -rf archive/
```

Verify deletion:
```bash
du -sh . # Should be ~20MB (down from 39MB)
```

Commit:
```bash
git add -A
git commit -m "chore: delete test artifacts and archive (19MB reduction)

- Remove scripts/captured_data/ (19MB of test screenshots)
- Remove captured_data/ directory
- Remove archive/ (192KB of old script versions)
- Fresh screenshots saved to cam-docs repo during actual usage"
```

---

## Task 10: Delete references/ Directory

Delete references/ directory since content is now embedded in sub-skills.

```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer
rm -rf references/
```

Verify:
```bash
ls -la # references/ should not exist
```

Commit:
```bash
git add -A
git commit -m "chore: delete references/ directory (content embedded in sub-skills)

- formatting-guide.md → embedded in cam-doc-formatter
- browser-automation.md → embedded in cam-browser-capture
- code-search.md → embedded in cam-code-searcher"
```

---

## Task 11: Refactor Main Skill as Dispatcher

Reduce main skill.md from 670 lines to ~100 lines, remove business logic, add sub-skill invocation.

**Create new skill.md:**
- Frontmatter: Update description to mention dispatcher
- Ask PM initial questions (feature name, available materials)
- Invoke cam-complexity-assessor
- Invoke cam-doc-structure-builder
- Content gathering: Ask user before invoking cam-browser-capture or cam-code-searcher
- Invoke cam-doc-formatter
- Invoke cam-doc-validator
- Pure orchestration, no business logic

Commit:
```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer
git add skill.md
git commit -m "refactor: convert main skill to lightweight dispatcher (670→100 lines)

- Remove all business logic
- Add sub-skill invocation using Skill tool
- Ask user confirmation before automation
- Pure orchestration pattern"
```

---

## Task 12: Update Main Skill README

Update README.md with new modular architecture.

**Update README.md:**
- Architecture diagram showing 1 main + 6 sub-skills
- Invocation flow
- Sub-skill descriptions
- Installation instructions

Commit:
```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer
git add README.md
git commit -m "docs: update README with modular architecture"
```

---

## Task 13: Update CHANGELOG

Add v4.0.0 entry to CHANGELOG.md.

**Add to CHANGELOG.md:**
```markdown
## [4.0.0] - 2026-03-04

### Breaking Changes

**Modular Architecture:**
- Split monolithic 670-line skill into 6 focused sub-skills
- Main skill now acts as lightweight dispatcher (100 lines)
- Each sub-skill has single responsibility

**Sub-Skills:**
- cam-complexity-assessor: Assess feature complexity
- cam-doc-structure-builder: Choose template and build outline
- cam-doc-formatter: Format content with inline validation
- cam-browser-capture: Browser automation + Python scripts
- cam-code-searcher: Search codebase for business logic
- cam-doc-validator: Comprehensive final validation

**Cleanup:**
- Deleted 19MB test artifacts (scripts/captured_data/)
- Deleted 192KB archive directory
- Deleted references/ (content embedded in sub-skills)
- Moved Python scripts to cam-browser-capture

**Impact:**
- Size: 39MB → 20MB (48% reduction)
- Main skill: 670 lines → 100 lines (85% reduction)
- Maintainability: Single responsibility per skill
```

Commit:
```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer
git add CHANGELOG.md
git commit -m "docs: add v4.0.0 changelog entry for modular architecture"
```

---

## Task 14: Test Sub-Skill Invocation

Test that main dispatcher can invoke each sub-skill using Skill tool.

**Test cam-complexity-assessor:**
```bash
# In Claude Code session
"Use cam-complexity-assessor skill to assess Time Selector feature"
```
Expected: Asks 3 questions, returns complexity level

**Test cam-doc-structure-builder:**
```bash
"Use cam-doc-structure-builder skill to build outline for Medium complexity feature"
```
Expected: Checks existing docs, suggests order number, builds outline

**Test cam-doc-formatter:**
```bash
"Use cam-doc-formatter skill to format this content: [sample content]"
```
Expected: Applies formatting rules, runs inline validation

**Test cam-browser-capture:**
```bash
"Use cam-browser-capture skill to capture screenshots from [URL]"
```
Expected: Runs Python script, captures screenshots

**Test cam-code-searcher:**
```bash
"Use cam-code-searcher skill to search for Time Selector business logic"
```
Expected: Searches i18n/frontend/backend, extracts logic

**Test cam-doc-validator:**
```bash
"Use cam-doc-validator skill to validate this document: [sample doc]"
```
Expected: Runs all validation checks, returns report

---

## Task 15: Test Python Scripts in New Location

Verify all Python scripts work after migration to cam-browser-capture/scripts/.

```bash
cd /Users/jessiecao/.claude/skills/cam-browser-capture/scripts

# Test auto_browse_cam_v3.py
python auto_browse_cam_v3.py --help

# Test explore_field_dependencies.py
python explore_field_dependencies.py --help

# Test browse_cam.py
python browse_cam.py --help

# Verify .auth/ directory exists
ls -la .auth/
```

Expected: All scripts run without import errors, .auth/ directory preserved

---

## Task 16: Run Existing Evals

Run existing evals to ensure no regression.

```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer
# Run evals if they exist
cat evals/evals.json
```

Expected: All evals pass, no regression from modular architecture

---

## Success Criteria

- ✅ 6 new sub-skill directories created
- ✅ Each sub-skill has skill.md + README.md
- ✅ Python scripts moved to cam-browser-capture/scripts/
- ✅ Test artifacts deleted (19MB reduction)
- ✅ Archive deleted (192KB reduction)
- ✅ References deleted (content embedded)
- ✅ Main skill refactored to ~100 lines
- ✅ README and CHANGELOG updated
- ✅ All sub-skills can be invoked independently
- ✅ Python scripts work in new location
- ✅ Existing evals pass (no regression)

**Final size:** ~20MB (down from 39MB, 48% reduction)
**Main skill:** ~100 lines (down from 670 lines, 85% reduction)
