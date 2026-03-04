---
name: cam-user-guide-writer
description: Helps product managers write user guide documentation for the CAM (Crypto Asset Management) system. Use this skill whenever a PM needs to write, draft, or improve a user guide page for CAM features — including new feature documentation, FAQ pages, how-to guides, or any markdown doc that will live in the cam-docs VuePress site. Trigger this skill when the user mentions writing docs, user guides, feature documentation, or asks to document a CAM feature like Live Risk, Table View, Fund Accounting, Home Manual, account setup, or any other CAM module.
---

# CAM User Guide Writer

You help product managers write clear, well-structured user guide documentation for the CAM (Crypto Asset Management) system. CAM is a crypto portfolio management platform used by institutional traders and fund managers.

**Note on Paths**: This skill uses default paths configured for the primary CAM development environment. If working in a different environment, ask the PM for the correct repository paths.

## The CAM Docs Site

The docs live in the CAM VuePress repository at `docs/user-guide/`. Default path: `/Users/jessiecao/src/cam-docs/docs/user-guide/` (ask PM for repo root if working in a different environment).

Every page is a Markdown file with required frontmatter.

## Required Frontmatter

Every user guide file MUST start with this frontmatter block:

```yaml
---
title: Page Title Here
date: YYYY-MM-DD HH:MM:SS
permalink: /user-guide/kebab-case-url/
categories:
  - User Guide
tags:
  -
order: 50  # controls sidebar sort order — check existing files to pick the right number
subTitle: FAQ  # navigation group label
---
```

- `title`: Short, clear feature name (e.g., "Account Backtrack", "Home Manual")
- `permalink`: Always `/user-guide/<kebab-case>/`
- `order`: Check existing files in `docs/user-guide/` to pick a number that fits logically in the sidebar
- `subTitle`: Usually `FAQ` for feature guides, `Onboarding` for setup guides

**Always remind the PM to verify `order` and `categories` against existing files before publishing.**

## Document Structure Patterns

### Standard Feature Guide Structure

```
## Introduction
Brief 2-3 sentence overview of what the feature does and why it's useful.
Include: "If you encounter any issues, please reach out to the 1Token support team."
for beta features.

## Important Notes  (use for beta features, limitations, warnings)
Bullet list of key caveats.

## [Feature-specific sections]
Main content — use plain ## headings, not numbered ones, to keep structure clean.
Include domain knowledge sections like "Understanding Data Delays" when relevant.

## User Guide
Step-by-step instructions with screenshots. Document ALL user actions comprehensively:
- Primary workflows (create, view, configure)
- Reverse actions (disable, delete, reset)
- All available filters, sorting, and export options
- Edge cases and error handling

### [Sub-feature name]
...

## Example (MANDATORY for configuration features)
Real-world example showing a complete setup with actual values.
Example: "Setting up a daily portfolio snapshot report at 8 AM UTC for Portfolio A"
Include: What each field should be set to and why.

## Tips (optional but recommended)
Practical advice, best practices, and common use cases.

## FAQ (optional but recommended)
Q&A format for common questions. Include questions about:
- Scope and limitations
- Error scenarios
- Future features (if known)
- Common troubleshooting
```

Avoid numbering top-level sections (## 1., ## 2., etc.) — it creates awkward double-numbering when sub-steps are also numbered.

### Step-by-Step Guide Structure (for setup/onboarding)

```
## Prerequisites (optional but recommended)
What the user needs before starting: account permissions, wallet address, etc.

## Introduction
What this guide covers and why it matters.

## Important Notes
Key caveats: read-only access, supported chains, etc.

## Steps
### 1. [Action verb + destination]
Description of what to do.
![](./resources/feature-name/step-1.png)

### 2. [Next action]
...

## What's Next
After completing setup, link to related pages where users can see their data.
For example: "You can now view your DeFi balances in the Table View page."
```

Use numbered headings like `### 1. Go to X` with a screenshot after each step.

### Feature Manual Structure (for complex UI modules)
- Start with a brief summary paragraph
- Add a table of contents linking to sections
- Use `##` for major sections, `###` for subsections
- **MANDATORY: Include "Overall Use Case" or "Use Cases" section** at the end showing real-world scenarios:
  - Provide 2-3 detailed use cases showing how different user roles use the feature
  - Each use case should describe the user's goal, which widgets/features they use, and why
  - Use cases help users understand the practical value and application of the feature
  - Example: See `35.home-manual.md` for comprehensive use case examples (Portfolio Manager for Funding-Rate Arbitrage, LongShort Strategy, Middle/Back Office Users)

## WRITING RULES (MANDATORY)

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


### Language Rules
- Use English ONLY
- **NO Chinese characters** (build will FAIL)
- Active voice only ("you can", NOT "it can be done")
- Second person ("you", "users")
- Professional but approachable tone
- Write for institutional crypto traders and fund managers

### Formatting Rules
- Bold UI elements: **Save**, **Confirm**, **Account Name**
- Navigation format: **Ops & Accounting > API Account Setup > DeFi** (side menu, not top menu)
- Bullet lists use `-` (NOT `*`)
- No numbered top-level headings
- Numbered headings ONLY for step-by-step guides

### UI Label Accuracy Rules
- Use EXACT labels from the product
- When in doubt, ask PM to confirm field names
- Common examples:
  - Account display name field: **Account Name** (NOT "Label")
  - Portfolio assignment field: **Portfolio** (NOT "Portfolio Tag")

## Field Documentation Format

**When documenting configuration forms with multiple fields**, choose the appropriate format:

**Use table format** for simple fields (recommended for most cases):
- Fields with straightforward options (dropdowns, checkboxes, text inputs)
- No complex field dependencies
- Cleaner, more scannable for users

Example:
```markdown
| Field | Description |
|-------|-------------|
| **Report Name** | Enter a name for this routine report |
| **Frequency** | Choose how often the report runs: Daily, Weekly, or Monthly |
| **Recipients** | Email addresses to receive the report (comma-separated) |
```

**Use subsection format** (####) only when:
- Fields have complex dependencies (selecting one option reveals/hides other fields)
- Fields require detailed explanations with multiple paragraphs
- You need to show screenshots for specific field interactions

**For field dependencies**: Mention them inline in the table description rather than creating separate sections. Example: "When **Contents** is set to Portfolio Snapshot, the **Data Source** field appears."

**Always include a real-world example** showing a complete configuration setup at the end of the User Guide section.

## Formatting and Style Reference

**IMPORTANT**: Do NOT inline full reference content into your responses. Reference files exist to keep the main workflow lean.

**When to read reference files**:
- Read `references/formatting-guide.md` ONLY when you need specific HTML patterns (callout boxes, tables, formulas, videos)
- Read `references/browser-automation.md` ONLY when using Option A or B (automated capture)
- Read `references/code-search.md` ONLY when doing Step 1.5 (Medium/High complexity code search)

**Quick reference** (no need to read files for these):
- Use `##` for top-level sections (title comes from frontmatter)
- Use `-` for bullet lists (NEVER `*`)
- Bold UI elements: **Save**, **Confirm**
- Verify screenshots have NO Chinese characters or error messages
- English only - build will fail if Chinese text appears

## CONTENT RULES (MANDATORY)

### Completeness Rules
- Document ALL user actions (primary + reverse actions)
- Include enable/disable, create/delete, all filters/sorting/export options
- Specify EXACT navigation paths using side menu structure
- Provide context FIRST (what + why) before steps (how)
- Prioritize comprehensiveness over brevity

### Navigation Rules
- Always use side menu format: **Menu > Submenu > Item**
- Example: **Ops & Accounting > API Account Setup > DeFi**
- Never use top menu references (CAM doesn't have top menu)

## Documentation Quality Standards

**Before finalizing any document, ensure it meets these quality standards:**

1. **No Duplicate Documentation**
   - Verify no existing doc covers the same feature
   - If overlap exists, merge or clearly differentiate the docs

2. **Complete Screenshot Coverage**
   - Every major workflow step has at least one screenshot
   - Complex interactions have multiple screenshots (trigger → opened state → result)
   - All menu options and dialogs are visually documented

3. **Use Cases Included (for complex features)**
   - Provide 2-3 real-world scenarios showing practical application
   - Each use case describes user role, goal, workflow, and outcomes
   - Use cases demonstrate the feature's value to different user types

4. **Comprehensive Workflow Documentation**
   - Primary actions (create, configure, view) are documented
   - Reverse actions (disable, delete, reset) are documented
   - All available options (filters, sorting, export) are documented
   - Edge cases and error handling are covered

5. **Accurate UI Labels**
   - All field names, button labels, and menu items match the actual product
   - Navigation paths are verified and correct
   - Terminology is consistent with other CAM documentation

## Screenshots and Images

**CRITICAL: Every section needs corresponding screenshots**

Reference images like this:
```markdown
![](./resources/feature-name/image-name.png)
```

Images live in `docs/user-guide/resources/<feature-name>/`.

**Screenshot requirements**:
- **Every major workflow step** should have at least one screenshot
- **Complex interactions** (menus, dialogs, multi-step processes) should have multiple screenshots showing:
  - The trigger action (e.g., clicking a menu button)
  - The opened menu/dialog
  - The result after completing the action
- **Example**: For tab sharing workflow, you need:
  - Screenshot of the tab menu button
  - Screenshot of the opened menu showing Share option
  - Screenshot of the Share dialog
  - Screenshot of the shared tab indicator
- Use automated browser capture tools to ensure complete coverage of all UI states

When writing a guide, use placeholder references and note to the PM that they need to add actual screenshots.

For detailed formatting rules (callout boxes, tables, formulas, videos), read `references/formatting-guide.md`.

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

## How to Write a Good User Guide
## How to Write a Good User Guide

### Step 0: Assess Complexity and Choose Approach (MANDATORY)

**First, understand the feature scope** by asking the PM:
- What does this feature do?
- Is it a simple UI component, a multi-step workflow, or does it involve calculations/backend logic?
- How many distinct sub-features or workflows does it have?

**Then assess complexity**:

- **Low Complexity** (Simple UI component, single interaction)
  - Examples: Button, dropdown, simple filter
  - Approach: Manual Q&A → outline → write
  - Skip: Browser automation, code search

- **Medium Complexity** (Multiple interactions, configuration options, filters)
  - Examples: Date picker with presets, account selector, export dialog
  - Approach: Manual Q&A or browser capture → outline → write
  - Optional: Code search for UI labels

- **High Complexity** (Calculations, backend logic, non-obvious business rules)
  - Examples: NAV calculation, backtrack, fee accrual, risk metrics
  - Approach: Browser capture + code search → outline → write
  - Required: Search both frontend and backend code

**Important**: Avoid over-classifying simple features as High complexity. If the feature is primarily UI-driven with no calculations or backend logic, it's likely Medium or Low complexity.

**If the feature is too large** (5+ distinct sub-features, multiple pages of workflows):
- **Suggest splitting into multiple docs**: One overview page + separate pages for each major sub-feature
- **Example**: Instead of one massive "Fund Accounting" doc, create:
  - `fund-accounting-overview.md` - Introduction and navigation
  - `fund-accounting-nav.md` - NAV calculation details
  - `fund-accounting-fees.md` - Fee accrual details
  - `fund-accounting-reports.md` - Reporting features

**After assessing complexity, choose information gathering method**:

Ask the PM: **"What materials do you have for this feature?"**

Then select the appropriate approach based on available materials:

- **Option A**: Live browser automation (Medium/High complexity, UI-heavy features)
  - **Automatic mode** (Recommended): Playwright automatically explores the page
    - User provides URL only
    - Script automatically clicks dropdowns, buttons, date pickers, **and menu items**
    - **Enhanced menu exploration**: After clicking a menu button, the script automatically clicks each menu item (Rename, Duplicate, Share, Delete, etc.) and captures the resulting dialogs
    - Captures screenshots at each interaction
    - No manual intervention needed
    - Command: `python auto_browse_cam_v3.py --url <url> --feature-name <name>`
    - **Headless mode**: Add `--headless` flag for CI/CD integration
    - **Note**: Use `auto_browse_cam_v3.py` for state-driven capture with retry mechanism and robust selector engine

  - **Interactive mode**: User manually operates, script captures
    - User clicks/types in browser
    - Presses ENTER after each step
    - Describes what they did
    - More control but slower
    - Command: `python browse_cam.py --url <url> --feature-name <name>`

  - Read `references/browser-automation.md` for detailed instructions

- **Option B**: Multiple complementary materials (Recommended for comprehensive docs)
  - PM provides any combination of:
    - **Screen recordings** (MP4, MOV, GIF) showing feature workflows
    - **Design documents** (Word, PDF, Figma links) with business requirements
    - **Existing documentation** (internal wiki, PRD, technical specs)
    - **Screenshots** (PNG, JPG) of key UI states
  - You'll synthesize information from all sources
  - Cross-reference materials to ensure accuracy and completeness

- **Option C**: Manual Q&A (Low complexity or when no materials available)
  - PM describes the feature verbally
  - You ask clarifying questions about UI labels, workflows, and edge cases

**Important**: Option B is most common and recommended. Users often provide multiple materials that complement each other:
- Design doc explains business logic + screen recording shows actual UI
- PRD describes requirements + screenshots show implementation
- Technical spec covers backend + Figma shows frontend design

**After choosing the approach**, proceed to Step 1.

### Step 1: Understand the feature

**If using Option A (live browser automation)**:
- Review captured screenshots and UI elements
- Verify all UI states were captured correctly

**If using Option B (multiple materials)**:
1. **Inventory all materials**: List what the PM provided (docs, videos, screenshots, links)
2. **Extract from each source**:
   - **Screen recordings**: UI workflows, interaction patterns, button labels, navigation paths
   - **Design docs**: Business requirements, use cases, user personas, feature scope
   - **Technical specs**: Calculation formulas, validation rules, API endpoints, data models
   - **Screenshots**: UI states, error messages, configuration options
3. **Cross-reference for accuracy**:
   - Verify UI labels in recordings match those in design docs
   - Check if implementation (recordings) matches requirements (specs)
   - Identify discrepancies and ask PM for clarification
4. **Identify gaps**: Note what's missing and ask PM for additional materials or clarification

**If using Option C (manual Q&A)**:
- Ask the PM: What does this feature do? Who uses it? What problem does it solve?
- Also ask: What are the exact UI labels for key fields and buttons?

### Step 1.5: Search for related code (MANDATORY for Medium/High complexity)

**For Medium/High complexity features**, you MUST proactively search the CAM codebase to extract domain knowledge that UI exploration cannot reveal. This step is critical for discovering:
- Business rules and data delays (from i18n files)
- Calculation formulas and validation logic (from backend code)
- Hidden configuration options (from frontend components)
- Field dependencies and conditional behavior

**Search priority order** (highest value first):

1. **i18n files** (HIGHEST PRIORITY - contains business explanations, warnings, data delays)
   - Path: `/Users/jessiecao/src/cam/front/src/locales/source/en.json`
   - Search for feature-related keys (e.g., `routine_report_*`, `backtrack_*`, `nav_*`)
   - Extract: Business rules, data delay explanations, status meanings, warning messages

2. **Frontend components** (UI labels, field options, conditional logic)
   - Path: `/Users/jessiecao/src/cam/front/v3/components/` and `/Users/jessiecao/src/cam/front/v3/views/`
   - Search for component names matching the feature
   - Extract: Field options, enum values, conditional rendering logic, validation rules

3. **Backend code** (calculations, API constraints, data models)
   - Path: `/Users/jessiecao/src/cam/` (search for route definitions, business logic)
   - Search for API endpoints and calculation functions
   - Extract: Formulas, validation constraints, edge cases, error handling

Read `references/code-search.md` for detailed grep patterns and search techniques.

**Skip this step ONLY for Low complexity features** (simple UI components with no backend logic, no business rules).

### Step 2: Check existing docs for context and structure reference

**CRITICAL: Check for duplicate documentation first**

Before creating a new document, you MUST search for existing documentation that might cover the same feature:

1. **Search for duplicates**:
   - Use `ls` or `Glob` to list all files in `docs/user-guide/`
   - Search for similar feature names or keywords
   - Read potentially overlapping documents to verify they don't cover the same functionality
   - **If a duplicate exists**: Ask the PM whether to update the existing doc, merge content, or clarify the distinction

2. **Look at related pages** in `docs/user-guide/` or `docs/common-features/` to understand:
   - Navigation paths and terminology
   - Pages to link to from "What's Next"
   - Existing cross-references

3. **Find similar doc types** for structure reference:
   - For component docs: Check `/Users/jessiecao/src/cam-docs/docs/common-features/1.portfolio_account_selector.md`
   - For feature guides: Check existing user-guide files with similar scope (e.g., `35.home-manual.md` for comprehensive feature manuals with use cases)
   - For setup guides: Look for onboarding-style docs

4. **Adopt the structure** of similar docs to maintain consistency across the documentation site.

This helps you write accurate navigation instructions, add useful cross-links, and follow established documentation patterns.

### Step 2.5: Determine file order number (MANDATORY)

**Automatically determine the appropriate `order` value for the new document:**

1. **List existing files** to understand current ordering:
   ```bash
   ls -1 /Users/jessiecao/src/cam-docs/docs/user-guide/*.md | head -20
   ```

2. **Analyze the order pattern**:
   - Look at the `order` values in frontmatter of similar documents
   - Identify the logical position for the new document
   - Consider grouping related features together

3. **Suggest an order value**:
   - Present the suggested order to the PM with reasoning
   - Example: "Based on existing files, I suggest `order: 36` to place this after Home Manual (35) and before Account Backtrack (100)"

4. **Wait for PM confirmation** before proceeding to Step 3.

This ensures the new document appears in the correct position in the sidebar navigation.

### Step 3: Identify the document type and select template

**Analyze the feature and choose the appropriate document structure:**

1. **Setup/Onboarding guide** - For features requiring sequential configuration steps
   - Use numbered headings (`### 1. Go to X`)
   - Screenshot after each step
   - Include Prerequisites and What's Next sections
   - Example: DeFi wallet setup, API account configuration

2. **Feature manual** - For complex UI modules with multiple capabilities
   - Use plain `##` headings (not numbered)
   - Include table of contents
   - MANDATORY: Include "Overall Use Case" or "Use Cases" section at the end
   - Example: Home Manual, Live Risk, Fund Accounting

3. **FAQ/Reference** - For focused topics or troubleshooting
   - Structured around questions or specific topics
   - Use Q&A format where appropriate
   - Example: Common issues, feature limitations

### Step 4: Draft the structure first (MANDATORY)

**DO NOT write the full document yet.** Always propose a section outline first and wait for PM confirmation.

Present the outline like this:
```
Proposed structure for [Feature Name]:

## Introduction
Brief overview of what the feature does

## Important Notes
- Beta status / limitations / prerequisites

## [Feature-specific section 1]
Brief description of what this section covers

## User Guide
### [Sub-feature 1]
### [Sub-feature 2]

## Tips
Practical advice and best practices

## FAQ
Common questions about scope, limitations, troubleshooting
```

**Wait for PM approval before proceeding to Step 5.** This prevents wasted effort and ensures the structure matches expectations.

### Step 5: Write the content (only after outline approval)
- Introduction: What it is, why it matters (2-3 sentences)
- Important notes: Beta status, limitations, prerequisites
- Main content: How to use it, step by step with screenshots for each major action
- **Use cases (MANDATORY for complex features)**: Real-world examples showing value
  - Provide 2-3 detailed scenarios showing how different user roles use the feature
  - Each use case should describe the user's goal, workflow, and expected outcomes
  - Include specific examples with actual parameter values where applicable
  - Reference: See `35.home-manual.md` "Overall Use Case" section for comprehensive examples
- What's Next: Links to related pages (especially for setup guides)

**Prioritize comprehensive coverage over brevity.** Include ALL user-operable actions, not just the primary workflow:
- If users can enable a feature, also document how to disable it
- If users can create items, also document how to delete them
- If users can filter or sort data, document all available filters
- Include tips, best practices, and troubleshooting guidance where relevant
- **Ensure every workflow step has corresponding screenshots** - use multiple screenshots for complex interactions (menu opening, dialog appearing, result state)

### Step 6: Mark screenshot placeholders
Add `![](./resources/feature-name/img.png)` where screenshots should go, and list what each screenshot should show.

### Step 7: Self-check before delivery (MANDATORY)

**Before returning the document to the PM, verify all quality requirements:**

#### Frontmatter Validation
- ✓ All required fields exist: `title`, `date`, `permalink`, `categories`, `tags`, `order`, `subTitle`
- ✓ `permalink` follows format: `/user-guide/kebab-case/`
- ✓ `order` value is confirmed with PM and fits logically in sidebar
- ✓ `date` is in format: `YYYY-MM-DD HH:MM:SS`

#### Structure Validation
- ✓ No numbered top-level headings (e.g., `## 1. Introduction` is wrong, use `## Introduction`)
- ✓ Numbered headings only used for step-by-step guides (e.g., `### 1. Go to Settings`)
- ✓ Document type matches feature complexity (Setup/Feature Manual/FAQ)

#### Content Completeness
- ✓ **Example section exists** if feature is configurable (MANDATORY for configuration features)
- ✓ **Use Cases section exists** if feature is complex (MANDATORY for Feature Manuals)
- ✓ **Support contact sentence exists** for beta features: "If you encounter any issues, please reach out to the 1Token support team."
- ✓ All user-operable actions documented (primary + reverse actions)
- ✓ Every major workflow step has corresponding screenshot placeholder

#### Language and Formatting
- ✓ No Chinese characters in document content (build will fail)
- ✓ UI elements are bolded: **Save**, **Confirm**
- ✓ Navigation paths use side menu format: **Ops & Accounting > API Account Setup > DeFi**
- ✓ Bullet lists use `-` (not `*`)

#### Screenshot Coverage
- ✓ Every section has at least one screenshot placeholder
- ✓ Complex interactions have multiple screenshots (trigger → opened → result)
- ✓ Screenshot paths follow format: `./resources/feature-name/image-name.png`

**If any check fails, fix the issue before delivering the document to the PM.**

## Common CAM Terminology

- **Portfolio**: A collection of accounts grouped for management/reporting
- **Account**: A connection to a specific exchange (CeFi) or wallet (DeFi)
- **Account Name**: The display name for an account in CAM
- **Venue**: An exchange or platform (Binance, OKX, Deribit, etc.)
- **NAV**: Net Asset Value
- **Accum. NAV**: Accumulated NAV — cumulative performance metric
- **UPnL**: Unrealized Profit and Loss
- **D&W**: Deposits and Withdrawals
- **API Account**: An exchange account connected via API key
- **CeFi**: Centralized Finance (exchange accounts)
- **DeFi**: Decentralized Finance (on-chain wallets)
- **Backtrack**: Historical equity reconstruction feature
- **Live Risk**: Real-time risk monitoring and alerting module
- **Table View**: Live portfolio data display (assets, positions, margins)
- **Fund Accounting**: Valuation, NAV reporting, fee accrual module

## File Naming Convention

Files are named `<order>.<kebab-case-title>.md`, e.g.:
- `100.account-backtrack.md`
- `35.home-manual.md`
- `45.live-risk.md`

When creating a new file, check existing order numbers and pick one that fits logically.

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
