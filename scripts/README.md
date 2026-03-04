# CAM Browser Automation Scripts

## Prerequisites

Install Playwright:

```bash
pip install playwright
playwright install chromium
```

## Usage

### Step 1: Start Chrome with Debugging Port

Open a terminal and run:

```bash
# macOS/Linux
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

# Or if chrome is in your PATH:
chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
```

### Step 2: Log into CAM

In the Chrome window that opened, navigate to CAM and log in normally.

### Step 3: Run the Capture Script

In another terminal:

```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts

# Navigate to a specific CAM feature page
python browse_cam.py --url https://your-cam-url.com/feature-page --feature-name portfolio-snapshot

# Or just use the current page
python browse_cam.py --feature-name portfolio-snapshot
```

### Step 4: Interactive Capture

The script will enter interactive mode:

1. Perform an action in the browser (click a button, fill a form, etc.)
2. Come back to the terminal and press ENTER
3. Describe what you just did
4. Repeat for each step
5. Type 'done' when finished

### Step 5: Review Captured Data

The script will save:
- `captured_data/<feature-name>_captured.json` - Structured data with all steps
- `captured_data/screenshots/` - Screenshots of each step

## Output Format

The captured JSON file contains:

```json
{
  "feature_name": "portfolio-snapshot",
  "capture_date": "2024-02-28T14:30:00",
  "total_steps": 3,
  "steps": [
    {
      "step_number": 1,
      "step_name": "step-1",
      "description": "Click Create Snapshot button",
      "url": "https://cam.example.com/portfolio",
      "title": "Portfolio - CAM",
      "screenshot": "step-1_20240228_143000.png",
      "buttons": [
        {"text": "Create Snapshot", "type": "button"},
        {"text": "Export", "type": "button"}
      ],
      "input_fields": [],
      "headings": [
        {"level": "H1", "text": "Portfolio Overview"}
      ]
    }
  ]
}
```

## Troubleshooting

### "Error connecting to browser"

Make sure Chrome is running with the debugging port:
```bash
chrome --remote-debugging-port=9222
```

### "Playwright is not installed"

Install it:
```bash
pip install playwright
playwright install chromium
```

### Port 9222 already in use

Use a different port:
```bash
chrome --remote-debugging-port=9223
python browse_cam.py --port 9223
```

## Field Dependencies Explorer Improvements (v2)

**Improvements from v1:**

1. **Baseline Comparison**: Changes are now detected against the initial baseline state, not the previous state in a chain. This prevents false negatives when a field returns to its original state.

2. **Complete Dropdown Data**: All dropdown options are now captured in the state, not just the selected value. This enables better analysis of available choices.

3. **Robust Wait Conditions**: Replaced fixed `wait_for_timeout()` calls with `wait_for_load_state("networkidle")` to handle dynamic content loading properly.

4. **Specific Error Handling**: Replaced bare `except:` blocks with specific exception types (`TimeoutError`, `AttributeError`) and added debug logging.

5. **Stratified Sampling**: Dropdown options are sampled using stratified approach (beginning, middle, end) instead of just the first 5, providing better coverage.

**Usage:**

```bash
python explore_field_dependencies.py --url <form-url> --output-dir <output-path>
```

## Field Dependencies Explorer V3 Improvements

**New in V3:**

1. **Structured State Changes**: Changes are now classified with semantic types for better interpretability:
   - `url_change`: Page navigation
   - `dialog_opened/closed`: Modal/dialog state changes
   - `field_added/removed`: Form field visibility changes
   - `field_modified`: Field value or property changes
   - `options_changed`: Dropdown option list changes
   - `validation_error`: Validation error appearance

2. **Global Exploration Budget**: Hard limits prevent exploration time explosion:
   - `max_steps`: Maximum interaction steps (default: 100)
   - `max_states`: Maximum unique states to visit (default: 50)
   - `max_time_seconds`: Maximum execution time (default: 300s)
   - `max_retries_per_action`: Retry limit per action (default: 3)

3. **Login Strong Signal Validation**: Multi-strategy login verification:
   - Home selector check (stable UI elements)
   - API endpoint verification (authenticated call)
   - Combined mode (both must pass)

## Login Validation (V3)

**Strong Signal Validation:**

The login process now uses multiple validation strategies:

1. **Home Selector Check**: Waits for stable UI elements (`.user-menu`, `[data-testid='user-profile']`)
2. **API Verification**: Calls `/api/user/info` to verify authenticated session
3. **Combined Mode**: Requires both checks to pass (configurable)

**Configuration:**

```python
validator = LoginValidator(
    home_selectors=[".user-menu"],
    api_endpoint="/api/user/info",
    require_both=True  # Strict mode
)
```

**Usage with Budget Control:**

```bash
python explore_field_dependencies.py --url <url> --max-steps 50 --max-time 180
```

**Programmatic Usage:**

```python
from explore_field_dependencies import FieldDependencyExplorer, ExplorationBudget

budget = ExplorationBudget(
    max_steps=50,
    max_states=30,
    max_time_seconds=180
)

explorer = FieldDependencyExplorer(budget=budget)
explorer.explore_dependencies(url)
```
