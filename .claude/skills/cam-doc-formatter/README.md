# CAM Doc Formatter

## Purpose

Write CAM user guide content with formatting rules and inline validation checks.

## What It Does

1. Applies markdown formatting rules (headings, lists, bold)
2. Formats screenshots and images correctly
3. Uses CAM terminology glossary
4. Performs inline validation checks:
   - No Chinese characters
   - UI elements bolded
   - Navigation format correct
   - Bullet lists use `-`
5. Catches obvious errors early before final validation

## Dependencies

Self-contained. No external dependencies.

## Returns

- Formatted markdown content
- Screenshot placeholders in correct locations
- Inline validation report
- List of any issues found

## Usage

This sub-skill is called during content writing to ensure proper formatting and catch errors early.
