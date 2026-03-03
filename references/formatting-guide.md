# Formatting Guide

## Formatting Checklist

Before publishing any document, verify it follows these rules:

**Markdown structure**:
- Use `##` for top-level sections (not `#` — the title comes from frontmatter)
- Use proper ordered lists: `1.`, `2.`, `3.` (NOT bold text like **1)**, **2)**, **3)**)
- Use `-` for bullet lists (NEVER use `*` as list marker)
- Don't add horizontal rules (`---`) after headings or below images

**Text formatting**:
- Bold UI elements: **"+ Add Account"**, **Save**, **Confirm**
- Use `**text**` for bold (NEVER use HTML `<b>` or `<strong>` tags)
- Use blank lines for paragraph breaks (NEVER use `<br/>` tags)

**Images**:
- Images must be on their own line, never embedded inline with text
- Use markdown syntax: `![alt text](image-path.png)` (NEVER use HTML `<img>` tags)
- Images are automatically centered when on their own line
- **CRITICAL: Verify screenshot content before using**:
  - NO Chinese characters visible in the screenshot
  - NO error messages, toasts, or warning dialogs visible
  - Screenshot shows the intended UI element (not wrong content)
  - If verification fails, recapture the screenshot with corrections

**Tables**:
- Use markdown table syntax for simple tables (NEVER use HTML `<table>` tags unless you need `rowspan` or complex layouts)

**Links**:
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
