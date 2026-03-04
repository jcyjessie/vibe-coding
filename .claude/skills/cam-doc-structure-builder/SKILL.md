---
name: cam-doc-structure-builder
description: Choose document template and build section outline for CAM user guide documentation
version: 1.0.0
---

# CAM Doc Structure Builder

This sub-skill helps determine the appropriate document template and builds a section outline for CAM user guide documentation.

## Process

### Step 1: Check existing docs for context

Before creating a new document structure, check for duplicates and understand existing patterns:

1. **Search for duplicates**:
   - List all files in `docs/user-guide/`
   - Search for similar feature names or keywords
   - Read potentially overlapping documents
   - **If a duplicate exists**: Ask the PM whether to update the existing doc, merge content, or clarify the distinction

2. **Look at related pages** in `docs/user-guide/` or `docs/common-features/` to understand:
   - Navigation paths and terminology
   - Pages to link to from "What's Next"
   - Existing cross-references

3. **Find similar doc types** for structure reference:
   - For component docs: Check `/Users/jessiecao/src/cam-docs/docs/common-features/1.portfolio_account_selector.md`
   - For feature guides: Check existing user-guide files with similar scope (e.g., `35.home-manual.md`)
   - For setup guides: Look for onboarding-style docs

### Step 2: Determine file order number

Automatically determine the appropriate `order` value for the new document:

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

### Step 3: Identify document type and select template

Analyze the feature and choose the appropriate document structure:

#### Template 1: Setup/Onboarding Guide
**Use for**: Features requiring sequential configuration steps

**Structure**:
```
## Prerequisites (optional but recommended)
What the user needs before starting

## Introduction
What this guide covers and why it matters

## Important Notes
Key caveats: read-only access, supported chains, etc.

## Steps
### 1. [Action verb + destination]
Description of what to do.
![](./resources/feature-name/step-1.png)

### 2. [Next action]
...

## What's Next
After completing setup, link to related pages
```

**Characteristics**:
- Use numbered headings (`### 1. Go to X`)
- Screenshot after each step
- Include Prerequisites and What's Next sections

**Examples**: DeFi wallet setup, API account configuration

#### Template 2: Feature Manual
**Use for**: Complex UI modules with multiple capabilities

**Structure**:
```
## Introduction
Brief 2-3 sentence overview of what the feature does and why it's useful.
Include support contact for beta features.

## Important Notes (use for beta features, limitations, warnings)
Bullet list of key caveats.

## [Feature-specific sections]
Main content — use plain ## headings, not numbered ones.
Include domain knowledge sections like "Understanding Data Delays" when relevant.

## User Guide
Step-by-step instructions with screenshots. Document ALL user actions:
- Primary workflows (create, view, configure)
- Reverse actions (disable, delete, reset)
- All available filters, sorting, and export options
- Edge cases and error handling

### [Sub-feature name]
...

## Example (MANDATORY for configuration features)
Real-world example showing a complete setup with actual values.

## Tips (optional but recommended)
Practical advice, best practices, and common use cases.

## Overall Use Case (MANDATORY for complex features)
2-3 detailed use cases showing how different user roles use the feature.
Each use case should describe the user's goal, workflow, and expected outcomes.

## FAQ (optional but recommended)
Q&A format for common questions.
```

**Characteristics**:
- Use plain `##` headings (not numbered)
- Include table of contents for long docs
- MANDATORY: Include "Overall Use Case" or "Use Cases" section at the end
- Avoid numbering top-level sections

**Examples**: Home Manual, Live Risk, Fund Accounting

#### Template 3: FAQ/Reference
**Use for**: Focused topics or troubleshooting

**Structure**:
```
## Introduction
Brief overview of the topic

## [Topic 1]
Content

## [Topic 2]
Content

## FAQ
Q&A format for common questions
```

**Characteristics**:
- Structured around questions or specific topics
- Use Q&A format where appropriate

**Examples**: Common issues, feature limitations

### Step 4: Build section outline

Present the outline to the PM and wait for approval:

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

## Example (if configurable)
Real-world setup example

## Tips
Practical advice and best practices

## Overall Use Case (if complex)
2-3 detailed scenarios showing value

## FAQ
Common questions about scope, limitations, troubleshooting
```

**Wait for PM approval before proceeding to content writing.**

## Output Format

Return the structure proposal in this format:

```
Document Type: [Setup Guide / Feature Manual / FAQ]

Suggested Order: [number]
Reasoning: [Why this order value fits logically]

Proposed Structure:
[Full section outline with brief descriptions]

Next Steps:
- Awaiting PM approval of structure
- Once approved, proceed to content writing
```
