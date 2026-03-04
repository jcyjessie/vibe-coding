# CAM Doc Validator

## Purpose

Comprehensive final quality check for CAM user guide documentation before delivery to PM.

## What It Does

1. Validates frontmatter (7 checks)
2. Validates structure (3 checks)
3. Validates content completeness (5 checks)
4. Validates language and formatting (4 checks)
5. Validates screenshot coverage (3 checks)
6. Generates validation report with pass/fail status
7. Fixes issues found during validation
8. Returns final report with recommendations

## Dependencies

Self-contained. No external dependencies.

## Returns

- Validation report with pass/fail status
- List of issues found with specific locations
- Recommended fixes for each issue
- List of fixes applied
- Recommendations for PM
- Final status (PASS / FAIL)

## Usage

This sub-skill is called as the final step before returning the document to the PM. It ensures all quality standards are met.

## Two-Phase Validation

- **Phase 1**: Inline validation during writing (by cam-doc-formatter)
- **Phase 2**: Final validation before delivery (by this sub-skill)
