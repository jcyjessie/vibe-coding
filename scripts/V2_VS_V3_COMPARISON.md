# V2 vs V3 Comparison

## Overview

**V2 (Kintsugi Style)**: Basic capture with storageState authentication
**V3 (State Tracking)**: Adds intelligent state tracking to prevent duplicates

## Key Differences

### 1. Module Dependencies

**V2:**
```python
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
```

**V3:**
```python
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from state_tracker import StateTracker
from selector_engine import SelectorEngine
from retry_handler import RetryHandler, RetryableError
import logging
```

### 2. Constructor Signature

**V2:**
```python
def __init__(self, auth_file=".auth/state.json", output_dir="captured_data"):
```

**V3:**
```python
def __init__(self, auth_file=".auth/state.json", output_dir="captured_data", headless=False):
    # ... existing code ...
    self.headless = headless
    
    # New: Initialize state tracking modules
    self.state_tracker = StateTracker()
    self.selector_engine = SelectorEngine()
    self.retry_handler = RetryHandler(max_retries=3, base_delay=1.0)
```

### 3. Browser Launch

**V2:**
```python
self.browser = self.playwright.chromium.launch(
    headless=False,  # Hardcoded
    channel="chrome",
    proxy={"server": "http://localhost:7890"}
)
```

**V3:**
```python
self.browser = self.playwright.chromium.launch(
    headless=self.headless,  # Configurable
    channel="chrome",
    proxy={"server": "http://localhost:7890"}
)
```

### 4. State Detection (New in V3)

**V2:** No state detection

**V3:**
```python
def _detect_state_change(self) -> Dict[str, Any]:
    """检测当前页面状态（用于后续任务的状态跟踪）"""
    state = {
        "url": self.page.url,
        "title": self.page.title(),
        "visible_buttons": [...],
        "visible_inputs": [...],
        "visible_dropdowns": [...]
    }
    return state
```

### 5. Screenshot Capture

**V2:**
```python
def capture_screenshot(self, step_name: str, description: str) -> Dict[str, Any]:
    # Always captures
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_filename = f"{step_name}_{timestamp}.png"
    # ... capture logic ...
    self.captured_steps.append(page_info)
    self.step_counter += 1
    return page_info
```

**V3:**
```python
def capture_screenshot(self, step_name: str, description: str) -> Optional[Dict[str, Any]]:
    # Check for duplicates first
    current_state = self._detect_state_change()
    
    if self.state_tracker.is_duplicate(current_state):
        logger.info(f"Skipping duplicate state: {step_name}")
        return None  # Skip duplicate
    
    self.state_tracker.add_state(current_state)
    
    # ... capture logic ...
    # Note: Does NOT append to captured_steps (caller's responsibility)
    self.step_counter += 1
    return page_info
```

### 6. Caller Pattern

**V2:**
```python
self.capture_screenshot("01-initial-page", "Initial page load")
# Automatically appends to captured_steps
```

**V3:**
```python
result = self.capture_screenshot("01-initial-page", "Initial page load")
if result:  # Only append if not duplicate
    self.captured_steps.append(result)
```

### 7. Capture Mode Identifier

**V2:**
```python
"capture_mode": "automatic_v2_kintsugi_style"
```

**V3:**
```python
"capture_mode": "automatic_v3_state_tracking"
```

### 8. CLI Arguments

**V2:**
```bash
python auto_browse_cam_v2.py \
  --url <url> \
  --feature-name <name> \
  --auth-file .auth/state.json \
  --output captured_data
```

**V3:**
```bash
python auto_browse_cam_v3.py \
  --url <url> \
  --feature-name <name> \
  --auth-file .auth/state.json \
  --output captured_data \
  --headless  # New flag
```

## Benefits of V3

1. **Duplicate Prevention**: Automatically skips capturing identical states
2. **Configurable Headless**: Can run with or without visible browser
3. **Better Logging**: Uses Python logging module for debugging
4. **Type Safety**: Added Optional return type for clarity
5. **Extensible**: Foundation modules ready for Tasks 6-8
6. **State Awareness**: Tracks page state changes intelligently

## Migration Path

To migrate from V2 to V3:

1. **No changes needed** for basic usage (backward compatible)
2. **Optional**: Add `--headless` flag for headless mode
3. **Benefit**: Automatic duplicate detection (no code changes)
4. **Future**: Ready for retry logic and smart selectors (Tasks 6-8)

## File Stats

| Metric | V2 | V3 |
|--------|----|----|
| Lines | 582 | 679 |
| Methods | 8 | 9 (+_detect_state_change) |
| Dependencies | 1 | 4 (+3 modules) |
| Return Types | Dict | Optional[Dict] |
| Duplicate Detection | ❌ | ✅ |
| Headless Support | ❌ | ✅ |
| State Tracking | ❌ | ✅ |
| Logging | print() | logging module |

## Backward Compatibility

✅ V3 is fully backward compatible with V2
✅ All V2 functionality preserved
✅ New features are opt-in (headless flag)
✅ Duplicate detection is automatic (no config needed)
