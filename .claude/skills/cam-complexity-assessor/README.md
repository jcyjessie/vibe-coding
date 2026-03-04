# CAM Complexity Assessor

## Purpose

Assess the complexity of CAM features to determine the appropriate documentation approach. This sub-skill helps classify features as Low, Medium, or High complexity based on their characteristics.

## Usage

This sub-skill is invoked by the main CAM user guide writer dispatcher at the beginning of the documentation workflow.

**Invocation**: The dispatcher calls this skill when a PM requests documentation for a new CAM feature.

**Process**:
1. Ask PM 3 sequential questions about the feature
2. Classify feature as Low/Medium/High complexity
3. Recommend appropriate documentation approach
4. Suggest feature splitting if needed

## Returns

The skill returns a structured assessment containing:

- **Complexity Rating**: Low, Medium, or High
- **Reasoning**: Explanation of the classification
- **Recommended Approach**: Information gathering method (Manual Q&A, Browser capture, or Browser + Code search)
- **Feature Splitting Recommendation**: Whether to split into multiple docs

## Assessment Questions

1. **Does this feature involve calculations or backend logic?** (Yes → High)
2. **Does it have multiple workflows or configuration options?** (Yes → Medium)
3. **Is it a simple UI component?** (Yes → Low)

## Examples

- **High**: NAV calculation, backtrack, fee accrual, risk metrics
- **Medium**: Date picker with presets, account selector, export dialog
- **Low**: Button, dropdown, simple filter, single-action dialog

## Integration

This sub-skill is part of the modularized CAM user guide writer system. It's the first step in the documentation workflow, helping to route features to the appropriate documentation strategy.
