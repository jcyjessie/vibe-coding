# CAM Browser Capture

## Purpose

Automate screenshot capture via browser automation for CAM user guide documentation.

## What It Does

1. Connects to Chrome with debug port
2. Navigates to CAM feature URL
3. Captures screenshots automatically or interactively
4. Extracts UI labels, buttons, input fields
5. Saves structured JSON data + screenshots

## Dependencies

- Playwright (Python library)
- Chrome with remote debugging port 9222
- Scripts: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/`
  - `auto_browse_cam.py` - Automatic capture
  - `browse_cam.py` - Interactive capture
  - Additional helper scripts
  - `.auth/` - Authentication state

## Returns

- `captured_data/<feature-name>_captured.json` - Structured data
- `captured_data/screenshots/` - All screenshots
- UI element inventory (buttons, inputs, dropdowns)

## Usage

This sub-skill is called for Medium/High complexity features to capture comprehensive UI workflows and screenshots.
