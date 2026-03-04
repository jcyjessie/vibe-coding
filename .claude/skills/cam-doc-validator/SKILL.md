---
name: cam-doc-validator
description: Comprehensive final quality check for CAM user guide documentation
version: 1.0.0
---

# CAM Doc Validator

This sub-skill performs comprehensive final quality checks on CAM user guide documentation before delivery.

## Two-Phase Validation Approach

### Phase 1: Inline Validation (During Writing)
Performed by cam-doc-formatter during content writing to catch obvious errors early.

### Phase 2: Final Validation (Before Delivery)
Performed by this sub-skill as the last step before returning the document to the PM.

## Validation Checklist

### 1. Frontmatter Validation (7 checks)

- ✓ Frontmatter block exists and is correctly formatted
- ✓ `title` field is present and concise (< 50 characters)
- ✓ `permalink` follows `/user-guide/kebab-case/` format
- ✓ `order` field is present (remind PM to verify against existing docs)
- ✓ `subTitle` is set (`FAQ` for features, `Onboarding` for setup)
- ✓ `date` is in `YYYY-MM-DD HH:MM:SS` format
- ✓ `categories` includes `User Guide`

### 2. Structure Validation (3 checks)

- ✓ No numbered top-level headings (e.g., `## 1. Introduction` is WRONG)
- ✓ Numbered headings only in step-by-step sections (e.g., `### 1. Go to Settings`)
- ✓ Document type matches feature complexity (Setup/Feature Manual/FAQ)

### 3. Content Completeness (5 checks)

- ✓ **Example section exists** if feature is configurable (MANDATORY for configuration features)
- ✓ **Use Cases section exists** if feature is complex (MANDATORY for Feature Manuals)
- ✓ **Support contact sentence** for beta features: "If you encounter any issues, please reach out to the 1Token support team."
- ✓ All user-operable actions documented (primary + reverse actions)
- ✓ Every major workflow step has screenshot placeholder

### 4. Language and Formatting (4 checks)

- ✓ **NO Chinese characters** in document content (build will FAIL)
- ✓ UI elements are bolded: **Save**, **Confirm**
- ✓ Navigation paths use side menu format: **Ops & Accounting > API Account Setup > DeFi**
- ✓ Bullet lists use `-` (NOT `*`)

### 5. Screenshot Coverage (3 checks)

- ✓ Every section has at least one screenshot placeholder
- ✓ Complex interactions have multiple screenshots (trigger → opened → result)
- ✓ Screenshot paths follow format: `./resources/feature-name/image-name.png`

## Validation Process

### Step 1: Run All Checks

Go through each checklist item systematically:

1. Read the document frontmatter
2. Verify all required fields exist and are correctly formatted
3. Check document structure (headings, lists, formatting)
4. Verify content completeness (examples, use cases, support contact)
5. Check language and formatting (no Chinese, UI bolded, navigation format)
6. Verify screenshot coverage (placeholders, paths, coverage)

### Step 2: Generate Validation Report

Create a structured report with:
- **Pass/Fail status** for each check
- **Issues found** with specific line numbers or sections
- **Recommended fixes** for each issue

### Step 3: Fix Issues (if any)

If any check fails:
1. Fix the issue immediately
2. Re-run validation to confirm fix
3. Document the fix in the validation report

### Step 4: Return Final Report

Return the validation report with:
- Overall status (PASS / FAIL)
- Detailed check results
- Any fixes applied
- Recommendations for PM

## Validation Report Format

```
CAM Doc Validation Report for [Feature Name]

Overall Status: [PASS / FAIL]

=== Frontmatter Validation ===
✓ Frontmatter block exists
✓ Title field present: "[Title]"
✓ Permalink format correct: /user-guide/[kebab-case]/
✓ Order field present: [number]
✓ SubTitle set: [value]
✓ Date format correct: YYYY-MM-DD HH:MM:SS
✓ Categories includes "User Guide"

=== Structure Validation ===
✓ No numbered top-level headings
✓ Numbered headings only in step-by-step sections
✓ Document type matches complexity: [Setup/Feature Manual/FAQ]

=== Content Completeness ===
✓ Example section exists (if configurable)
✓ Use Cases section exists (if complex)
✓ Support contact sentence (if beta)
✓ All user actions documented
✓ Screenshot placeholders present

=== Language and Formatting ===
✓ No Chinese characters
✓ UI elements bolded
✓ Navigation format correct
✓ Bullet lists use `-`

=== Screenshot Coverage ===
✓ Every section has screenshots
✓ Complex interactions have multiple screenshots
✓ Screenshot paths correct

=== Issues Found ===
[If any issues found, list them here with specific locations and recommended fixes]

=== Fixes Applied ===
[List any fixes that were applied during validation]

=== Recommendations for PM ===
- Verify `order` value against existing docs
- Add actual screenshots to replace placeholders
- [Any other recommendations]

Final Status: [PASS / FAIL]
```

## Common Issues and Fixes

### Issue: Chinese characters in content
**Fix**: Replace with English text or remove

### Issue: UI elements not bolded
**Fix**: Wrap in `**text**` markdown

### Issue: Navigation format incorrect
**Fix**: Use side menu format: **Menu > Submenu > Item**

### Issue: Bullet lists use `*` instead of `-`
**Fix**: Replace all `*` list markers with `-`

### Issue: Missing Example section for configurable feature
**Fix**: Add Example section with real-world setup

### Issue: Missing Use Cases section for complex feature
**Fix**: Add Use Cases section with 2-3 detailed scenarios

### Issue: Missing support contact for beta feature
**Fix**: Add to Introduction: "If you encounter any issues, please reach out to the 1Token support team."

### Issue: Numbered top-level headings
**Fix**: Remove numbers from top-level headings (keep only for step-by-step guides)

### Issue: Screenshot placeholders missing
**Fix**: Add placeholders for each major workflow step

### Issue: Screenshot paths incorrect
**Fix**: Use format: `./resources/feature-name/image-name.png`

## Output Length Check

Verify document length matches feature complexity:
- Small feature: 400–800 words
- Medium feature: 800–1500 words
- Complex feature: 1500–2500 words
- If > 2500 words, suggest splitting into multiple docs

## Final Checklist Before Delivery

Before returning the document to the PM:

1. ✓ All validation checks passed
2. ✓ All issues fixed
3. ✓ Validation report generated
4. ✓ Document length appropriate
5. ✓ Screenshot placeholders noted
6. ✓ PM recommendations included

**If ANY check fails, FIX the issue before delivering the document.**
