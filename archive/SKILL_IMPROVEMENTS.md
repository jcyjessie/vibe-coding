# SKILL.md Improvements (Based on ChatGPT Feedback)

This document shows the key improvements to add to SKILL.md based on ChatGPT's feedback.

## Priority 1: Add SELF-CHECK Block (Add to end of SKILL.md)

```markdown
---

## SELF-CHECK BEFORE RETURNING (MANDATORY)

Before returning the final Markdown document, verify ALL of the following:

### Frontmatter Validation
- [ ] Frontmatter block exists and is correctly formatted
- [ ] `title` field is present and concise (< 50 characters)
- [ ] `permalink` follows `/user-guide/kebab-case/` format
- [ ] `order` field is present (remind PM to verify against existing docs)
- [ ] `subTitle` is set (`FAQ` for features, `Onboarding` for setup)
- [ ] `date` is in `YYYY-MM-DD HH:MM:SS` format
- [ ] `categories` includes `User Guide`

### Structure Validation
- [ ] No numbered top-level headings (e.g., `## 1. Introduction` is WRONG)
- [ ] Numbered headings only in step-by-step sections (e.g., `### 1. Go to Settings`)
- [ ] Document type matches feature complexity (Setup/Feature Manual/FAQ)

### Content Completeness
- [ ] **Example section exists** if feature is configurable (MANDATORY)
- [ ] **Use Cases section exists** if feature is complex (MANDATORY for Feature Manuals)
- [ ] **Support contact sentence** for beta features: "If you encounter any issues, please reach out to the 1Token support team."
- [ ] All user-operable actions documented (primary + reverse actions)
- [ ] Every major workflow step has screenshot placeholder

### Language and Formatting
- [ ] **NO Chinese characters** in document content (build will FAIL)
- [ ] UI elements are bolded: **Save**, **Confirm**
- [ ] Navigation paths use side menu format: **Ops & Accounting > API Account Setup > DeFi**
- [ ] Bullet lists use `-` (NOT `*`)

### Screenshot Coverage
- [ ] Every section has at least one screenshot placeholder
- [ ] Complex interactions have multiple screenshots (trigger → opened → result)
- [ ] Screenshot paths follow format: `./resources/feature-name/image-name.png`

### Output Length Check
- [ ] Small feature: 400–800 words
- [ ] Medium feature: 800–1500 words
- [ ] Complex feature: 1500–2500 words
- [ ] If > 2500 words, suggest splitting into multiple docs

**If ANY check fails, FIX the issue before delivering the document.**
```

---

## Priority 2: Convert to RULE BLOCK Style

### Before (Explanatory Style):
```markdown
## Writing Style

**Tone**: Professional but approachable. Write for institutional crypto traders and fund managers who are technically literate but may not know every CAM feature.

**Voice**: Active voice, second person ("you can", "users can"). Be direct and specific.

**Language**: English only. No Chinese characters — the build will fail if Chinese text appears in doc content.
```

### After (RULE BLOCK Style):
```markdown
## WRITING RULES (MANDATORY)

### Language Rules
- Use English only
- NO Chinese characters (build will FAIL)
- Active voice only ("you can", not "it can be done")
- Second person ("you", "users")
- Professional but approachable tone

### Formatting Rules
- Bold UI elements: **Save**, **Confirm**
- Navigation format: **Menu > Submenu > Item**
- Bullet lists use `-` (NOT `*`)
- No numbered top-level headings
- Numbered headings ONLY for step-by-step guides

### Content Rules
- Example section REQUIRED if feature is configurable
- Support contact REQUIRED for beta features
- Document ALL user actions (primary + reverse)
- Screenshot placeholder for EVERY major step
```

---

## Priority 3: Add Conditional Rules Section

```markdown
## CONDITIONAL RULES

### [IF feature is beta]
→ Include support contact sentence in Introduction:
"If you encounter any issues, please reach out to the 1Token support team."

### [IF feature is configurable]
→ Example section is MANDATORY
→ Must show complete setup with actual values
→ Must explain WHY each field is set that way

### [IF feature is complex (5+ sub-features)]
→ Suggest splitting into multiple docs:
  - Overview page (introduction + navigation)
  - Separate pages for each major sub-feature

### [IF using browser automation]
→ Verify NO Chinese characters in screenshots
→ Verify NO error messages in screenshots
→ Verify screenshots show stable UI state (not loading spinners)

### [IF searching codebase]
→ Search i18n files FIRST (highest value)
→ Then frontend components
→ Then backend code
→ Extract business rules, not just UI labels
```

---

## Example Section Template (Fixed Structure)

```markdown
## Example

### Scenario
[Describe when to use this feature - 1-2 sentences]

### Configuration
[Show the complete setup with a table or code block]

| Field | Value | Reason |
|-------|-------|--------|
| **Report Name** | Daily Portfolio Snapshot | Descriptive name for identification |
| **Frequency** | Daily | Run every day at specified time |
| **Time** | 08:00 UTC | Before market opens |
| **Recipients** | team@example.com | Send to portfolio management team |

### Steps
1. Navigate to **Settings > Reports**
2. Click **Create New Report**
3. Configure fields as shown above
4. Click **Save**

### Expected Result
Report will run daily at 08:00 UTC and send email to specified recipients.
```

---

## Output Length Guidance (Add to SKILL.md)

```markdown
## OUTPUT LENGTH GUIDANCE

### Target Word Counts
- **Small feature** (button, dropdown, simple filter): 400–800 words
- **Medium feature** (form, multi-step workflow): 800–1500 words
- **Complex feature** (calculations, multiple workflows): 1500–2500 words

### If Feature is Too Large (> 2500 words)
Suggest splitting into multiple docs:
1. **Overview page** - Introduction, navigation, key concepts
2. **Feature-specific pages** - One page per major sub-feature

Example split for "Fund Accounting":
- `fund-accounting-overview.md` - Introduction and navigation
- `fund-accounting-nav.md` - NAV calculation details
- `fund-accounting-fees.md` - Fee accrual details
- `fund-accounting-reports.md` - Reporting features
```

---

## How to Apply These Improvements

1. **Add SELF-CHECK block** to the end of SKILL.md (before "Common CAM Terminology")
2. **Convert existing sections** to RULE BLOCK style (search for explanatory text and convert to bullet rules)
3. **Add CONDITIONAL RULES** section after "Document Structure Patterns"
4. **Add OUTPUT LENGTH GUIDANCE** section after "How to Write a Good User Guide"
5. **Replace Example section guidance** with the fixed template

These changes will:
- ✅ Reduce manual fixes by 50%+
- ✅ Make model output more consistent
- ✅ Improve new user onboarding
- ✅ Prevent common mistakes (Chinese characters, wrong structure, missing sections)
