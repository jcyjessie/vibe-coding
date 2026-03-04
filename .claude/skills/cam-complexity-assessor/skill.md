---
name: cam-complexity-assessor
description: Assess CAM feature complexity by asking PMs 3 questions to determine if a feature is Low/Medium/High complexity
version: 1.0.0
---

# CAM Complexity Assessor

This sub-skill assesses the complexity of CAM features to help determine the appropriate documentation approach.

## Assessment Process

Ask the PM these 3 questions in order:

### Question 1: Does this feature involve calculations or backend logic?
- **Examples**: NAV calculation, backtrack, fee accrual, risk metrics, P&L computation
- **If YES** → **High Complexity**
- **If NO** → Continue to Question 2

### Question 2: Does it have multiple workflows or configuration options?
- **Examples**: Date picker with presets, account selector with filters, export dialog with format options
- **If YES** → **Medium Complexity**
- **If NO** → Continue to Question 3

### Question 3: Is it a simple UI component?
- **Examples**: Button, dropdown, simple filter, single-action dialog
- **If YES** → **Low Complexity**
- **If NO** → Re-assess with PM (may be Medium)

## Complexity Criteria

### High Complexity
**Characteristics**:
- Involves calculations or backend logic
- Non-obvious business rules
- Requires understanding both frontend and backend code

**Examples**:
- NAV calculation
- Backtrack functionality
- Fee accrual system
- Risk metrics computation
- Portfolio rebalancing logic

**Documentation Approach**:
- Browser capture + code search required
- Search both frontend and backend code
- Deep dive into business logic

### Medium Complexity
**Characteristics**:
- Multiple interactions or workflows
- Configuration options or filters
- UI-driven with some complexity

**Examples**:
- Date picker with presets
- Account selector with filters
- Export dialog with format options
- Multi-step wizards
- Forms with conditional fields

**Documentation Approach**:
- Manual Q&A or browser capture
- Optional code search for UI labels
- Focus on user workflows

### Low Complexity
**Characteristics**:
- Simple UI component
- Single interaction
- No calculations or backend logic

**Examples**:
- Button
- Dropdown
- Simple filter
- Single-action dialog
- Basic toggle

**Documentation Approach**:
- Manual Q&A → outline → write
- Skip browser automation and code search
- Quick documentation turnaround

## Important Guidelines

1. **Avoid over-classification**: If the feature is primarily UI-driven with no calculations or backend logic, it's likely Medium or Low complexity, not High.

2. **Feature splitting**: If the feature is too large (5+ distinct sub-features, multiple pages of workflows):
   - Suggest splitting into multiple docs
   - Create one overview page + separate pages for each major sub-feature
   - Example: Instead of one massive "Fund Accounting" doc, create:
     - `fund-accounting-overview.md` - Introduction and navigation
     - `fund-accounting-nav.md` - NAV calculation details
     - `fund-accounting-fees.md` - Fee accrual details
     - `fund-accounting-reports.md` - Reporting features

## Output Format

Return the assessment in this format:

```
Complexity Assessment: [Low/Medium/High]

Reasoning:
- [Brief explanation of why this complexity level was chosen]
- [Key factors that influenced the decision]

Recommended Approach:
- [Information gathering method: Manual Q&A / Browser capture / Browser + Code search]
- [Any specific considerations for this feature]

Feature Splitting Recommendation:
- [If applicable, suggest how to split the feature into multiple docs]
- [Otherwise, state "No splitting needed"]
```
