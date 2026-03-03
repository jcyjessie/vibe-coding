# Browser Automation Guide

The skill includes browser automation scripts that connect to your already-logged-in Chrome browser to capture CAM workflows.

## Two Modes Available

### Mode 1: Automatic Capture (Recommended)

**Fully automated** - Just provide URL, script does everything:

```bash
python auto_browse_cam.py --url <cam-url> --feature-name <name>
```

**What it does automatically**:
1. Navigates to the URL
2. Captures initial page state
3. Finds and clicks dropdowns, buttons, date pickers
4. Captures screenshot after each interaction
5. Extracts UI labels, button text, input fields
6. Saves all data to JSON

**Best for**: Standard CAM features with common UI patterns (dropdowns, date pickers, filters)

### Mode 2: Interactive Capture

**Semi-automatic** - You operate, script captures:

```bash
python browse_cam.py --url <cam-url> --feature-name <name>
```

**How it works**:
1. You manually click/type in the browser
2. Press ENTER after each step
3. Describe what you did
4. Type 'done' when finished

**Best for**: Complex workflows, custom interactions, or when automatic mode misses elements

## Prerequisites

```bash
# Install Playwright
pip install playwright
playwright install chromium
```

## Quick Start

### Step 1: Start Chrome with debugging port

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Linux
chrome --remote-debugging-port=9222

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

### Step 2: Log into CAM

In the Chrome window that just opened, navigate to CAM and log in.

### Step 3: Run the capture script

**For automatic capture** (recommended):

```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts
python auto_browse_cam.py --url https://cam.cammaster.org/v3/analysis/reporting/routine --feature-name routine-report
```

**For interactive capture**:

```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts
python browse_cam.py --url https://cam.cammaster.org/v3/analysis/reporting/routine --feature-name routine-report
```

### Step 4: Review output

Output files:
- `captured_data/<feature-name>_captured.json` - Structured data
- `captured_data/screenshots/` - All screenshots

## Automatic Capture Details

The automatic script explores the page in 3 phases:

**Phase 1: Initial State**
- Captures page load
- Extracts all visible buttons, inputs, dropdowns

**Phase 2: Interactive Elements**
- Automatically finds and clicks:
  - Date/time pickers
  - Dropdowns and selects
  - Filter buttons
  - Export buttons
  - Settings buttons
- Captures screenshot after each interaction

**Phase 3: Modals/Dialogs**
- Detects any open modals
- Captures their content

## Interactive Capture Details

**Process**:
1. Script navigates to URL
2. You perform actions in browser
3. Press ENTER to capture current state
4. Type description of what you did
5. Repeat until done
6. Type 'done' to finish

**Output**: Same JSON format as automatic mode

## Troubleshooting

### Chrome connection fails
- Check Chrome is running with `--remote-debugging-port=9222`
- Check no other process is using port 9222
- Try closing all Chrome windows and restarting

### Automatic mode misses elements
- Use interactive mode for more control
- Or modify `auto_browse_cam.py` to add custom selectors

### Screenshots are blank
- Wait longer for page to load (increase `wait_for_timeout`)
- Check if elements are actually visible
- Try interactive mode to capture at the right moment

### Chinese characters in screenshots
- Set CAM UI language to English before capturing
- The skill will detect Chinese characters and warn you

## Advanced Usage

### Custom selectors for automatic mode

Edit `auto_browse_cam.py` and add to `selectors_to_try`:

```python
selectors_to_try = [
    # Your custom selectors
    ("[data-testid='my-custom-element']", "custom element"),
    ("button:has-text('My Button'):visible", "my button"),
]
```

### Capture specific element

In interactive mode, use browser DevTools to inspect and click the exact element you want to capture.

## Output Format

Both modes produce the same JSON structure:

```json
{
  "feature_name": "routine-report",
  "capture_date": "2026-03-02T10:30:00",
  "capture_mode": "automatic",
  "total_steps": 5,
  "steps": [
    {
      "step_number": 1,
      "step_name": "01-initial-page",
      "description": "Initial page load",
      "url": "https://cam.cammaster.org/...",
      "title": "Routine Report",
      "screenshot": "01-initial-page_20260302_103000.png",
      "buttons": ["Export", "Filter", "Refresh"],
      "input_fields": [...],
      "dropdowns": [...]
    }
  ]
}
```

## Benefits

**Automatic mode**:
- ✅ Fast (no manual interaction)
- ✅ Consistent (same elements every time)
- ✅ Complete (finds all common UI patterns)
- ✅ Hands-free (just provide URL)

**Interactive mode**:
- ✅ Precise control over what to capture
- ✅ Can capture complex workflows
- ✅ Can add custom descriptions
- ✅ Works when automatic mode misses elements
