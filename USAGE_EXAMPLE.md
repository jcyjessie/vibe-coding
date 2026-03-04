# CAM User Guide Writer - Usage Examples

This document shows two real-world examples of using the skill.

---

## Example 1: Simple Feature (Low Complexity)

**Feature:** Time Selector component

**Complexity:** Low - Simple UI component with dropdown options

### Workflow

**User:** "I need to write a user guide for the Time Selector component"

**Assistant:**
- Assesses complexity: Low (simple UI component)
- Chooses approach: Manual Q&A (Option C)
- Asks clarifying questions about the component

**Questions Asked:**
- What does the Time Selector do?
- What time range options are available?
- Where is it used in CAM?
- Are there any limitations?

**Output:**
- 600-word documentation
- Structure: Introduction → User Guide → Tips
- No Example section needed (not configurable)
- 3 screenshot placeholders

**Time:** ~10 minutes from start to final document

---

## Example 2: Complex Feature (High Complexity)

**Feature:** Routine Report Settings

**Complexity:** High - Configuration form with calculations, scheduling, multiple field dependencies

### Workflow

**User:** "I need to write a user guide for Routine Report Settings"

**Assistant:**
- Assesses complexity: High (calculations, dependencies, backend logic)
- Chooses approach: Browser capture + Code search (Option A + Code)
- Guides browser automation setup

**Information Gathering:**

1. **Browser Capture** (Option A - Automatic mode):
   ```bash
   python auto_browse_cam.py --url https://cam.1token.trade/v3/settings/reports --feature-name routine-report-settings
   ```
   - Captures 12 screenshots
   - Extracts UI labels and field options
   - Records interaction flows

2. **Code Search** (Step 1.5):
   - Searches i18n files for business rules
   - Finds data delay explanations
   - Discovers validation constraints
   - Extracts calculation formulas

**Output:**
- 1,800-word documentation
- Structure: Introduction → Important Notes → Understanding Data Delays → User Guide → Example → Tips → FAQ
- **Example section included** (configurable feature - MANDATORY)
- 12 screenshots with accurate labels
- Business rules documented from code

**Time:** ~30 minutes from start to final document

---

## Key Differences

| Aspect | Simple Feature | Complex Feature |
|--------|---------------|-----------------|
| **Complexity** | Low | High |
| **Approach** | Manual Q&A | Browser capture + Code search |
| **Word Count** | 600 words | 1,800 words |
| **Screenshots** | 3 | 12 |
| **Example Section** | Not needed | MANDATORY |
| **Code Search** | Skipped | Required (i18n + frontend + backend) |
| **Time** | 10 minutes | 30 minutes |

---

## When to Use Each Approach

### Manual Q&A (Option C)
**Use for:**
- Simple UI components (buttons, dropdowns, filters)
- Features with no calculations or backend logic
- Quick documentation updates

**Example features:**
- Time Selector
- Account Selector
- Simple filters

### Browser Capture (Option A)
**Use for:**
- Multi-step workflows
- Forms with many fields
- Features requiring accurate UI labels

**Example features:**
- Account setup wizards
- Configuration forms
- Multi-page workflows

### Browser Capture + Code Search (Option A + Code)
**Use for:**
- Features with calculations
- Complex business rules
- Backend logic that affects UI
- Data delays or constraints

**Example features:**
- Routine Report Settings
- NAV Calculation
- Backtrack
- Fee Accrual

---

## Tips for Success

1. **Assess complexity first** - Don't over-engineer simple features
2. **Use browser automation for accuracy** - Reduces manual fixes by 50%
3. **Always search i18n files** for Medium/High complexity - Contains business rules
4. **Include Example section** for configurable features - MANDATORY
5. **Check SELF-CHECK list** before delivering - Catches 90% of issues

---

## Common Mistakes to Avoid

❌ **Don't:** Use browser automation for simple buttons
✅ **Do:** Use manual Q&A for simple features

❌ **Don't:** Skip code search for complex features
✅ **Do:** Search i18n → frontend → backend for business rules

❌ **Don't:** Forget Example section for configurable features
✅ **Do:** Always include real-world setup example

❌ **Don't:** Number top-level headings (## 1., ## 2.)
✅ **Do:** Use plain headings (## Introduction, ## User Guide)

❌ **Don't:** Include Chinese characters in docs
✅ **Do:** Use English only (build will fail otherwise)

---

For detailed automation setup, see [AUTO_CAPTURE_GUIDE.md](./AUTO_CAPTURE_GUIDE.md).

For complete rules and constraints, see [SKILL.md](./SKILL.md).
