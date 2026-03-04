---
name: cam-doc-formatter
description: Write CAM user guide content with formatting rules and inline validation checks
version: 1.0.0
---

# CAM Doc Formatter

This sub-skill writes CAM user guide content with proper formatting rules and performs inline validation checks.

## Formatting Rules

### Markdown Structure
- Use `##` for top-level sections (not `#` — the title comes from frontmatter)
- Use proper ordered lists: `1.`, `2.`, `3.` (NOT bold text like **1)**, **2)**, **3)**)
- Use `-` for bullet lists (NEVER use `*` as list marker)
- Don't add horizontal rules (`---`) after headings or below images

### Text Formatting
- Bold UI elements: **"+ Add Account"**, **Save**, **Confirm**
- Use `**text**` for bold (NEVER use HTML `<b>` or `<strong>` tags)
- Use blank lines for paragraph breaks (NEVER use `<br/>` tags)

### Images
- Images must be on their own line, never embedded inline with text
- Use markdown syntax: `![alt text](image-path.png)` (NEVER use HTML `<img>` tags)
- Images are automatically centered when on their own line
- **CRITICAL: Verify screenshot content before using**:
  - NO Chinese characters visible in the screenshot
  - NO error messages, toasts, or warning dialogs visible
  - Screenshot shows the intended UI element (not wrong content)
  - If verification fails, recapture the screenshot with corrections

### Tables
- Use markdown table syntax for simple tables (NEVER use HTML `<table>` tags unless you need `rowspan` or complex layouts)

### Links
- Reference other docs with markdown links

## Screenshots and Images

Reference images like this:
```markdown
![](./resources/feature-name/image-name.png)
```

Images live in `docs/user-guide/resources/<feature-name>/`. When writing a guide, use placeholder references like `![](./resources/feature-name/img.png)` and note to the PM that they need to add actual screenshots.

For GIFs (animated interactions): `![](./resources/feature-name/animation.gif)`

For side-by-side images:
```html
<div style="margin-top: 15px; display: flex; justify-content: space-around;">
  <img src="./resources/feature-name/img-left.png" width="45%" />
  <img src="./resources/feature-name/img-right.png" width="45%" />
</div>
```

## Info/Tip Callout Box

Use this HTML pattern for tips, support notes, or important callouts:

```html
<div style="padding:10px;
    border:1px solid #EFE2CE;
    border-radius:5px;
    background:#fbf4eb;">
  <span style="font-size: 20px;">💡</span>
  <span style="font-style:italic;color: #1b1b1b">Your tip text here.</span>
</div>
```

For success/use-case callouts (green):
```html
<div style="padding:10px;margin-top: 10px;
    border:1px solid #b7edb1;
    border-radius:5px;
    background: #f0fbef; display: flex">
  <div style="font-size: 20px;">✅</div>
  <div style="margin-left: 10px;">Use case content here.</div>
</div>
```

## Tables

For feature comparison or support matrices, use HTML tables (not Markdown tables) when you need `rowspan` or complex layouts:

```html
<table>
  <thead>
    <tr>
      <th>Column 1</th>
      <th>Column 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Value</td>
      <td>Value</td>
    </tr>
  </tbody>
</table>
```

For simple tables, Markdown tables are fine:
```markdown
| Column 1 | Column 2 |
| --- | --- |
| Value | Value |
```

## Math Formulas

Use LaTeX syntax wrapped in `$$` for block formulas:
```
$$\text{Equity Valuation} = \sum \text{(Nominal Value of Spot)}$$
```

## Embedded Videos

For Guidde or other embedded tutorial videos:
```html
<iframe
  src="https://embed.app.guidde.com/playbooks/YOUR_ID?mode=videoOnly"
  width="100%"
  height="535"
  frameborder="0"
  allowfullscreen>
</iframe>
```

## CAM Terminology Glossary

Use these exact terms when writing CAM documentation:

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

## Inline Validation Checks

Before returning content, perform these checks:

### Language Check
- ✓ No Chinese characters in document content (build will fail)
- ✓ English only throughout

### Formatting Check
- ✓ UI elements are bolded: **Save**, **Confirm**
- ✓ Navigation paths use side menu format: **Ops & Accounting > API Account Setup > DeFi**
- ✓ Bullet lists use `-` (not `*`)
- ✓ No HTML tags for bold/breaks (use markdown)

### Screenshot Check
- ✓ Every section has at least one screenshot placeholder
- ✓ Screenshot paths follow format: `./resources/feature-name/image-name.png`
- ✓ Complex interactions have multiple screenshots (trigger → opened → result)

### Structure Check
- ✓ Top-level sections use `##` (not `#`)
- ✓ No numbered top-level headings (unless step-by-step guide)
- ✓ Proper list formatting (ordered vs unordered)

## Writing Style

- Use English ONLY
- Active voice only ("you can", NOT "it can be done")
- Second person ("you", "users")
- Professional but approachable tone
- Write for institutional crypto traders and fund managers

## Navigation Format

Always use side menu format for navigation paths:
- **Ops & Accounting > API Account Setup > DeFi** (CORRECT)
- Never use top menu references (CAM doesn't have top menu)

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

## Output Format

Return the formatted content with:
1. Proper markdown structure
2. All formatting rules applied
3. Screenshot placeholders in correct locations
4. Inline validation checks passed
5. Note any issues found during validation
