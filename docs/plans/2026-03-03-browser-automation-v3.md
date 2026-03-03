# Browser Automation V3 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade CAM browser automation scripts from v2 to v3 with state-driven capture, robust selectors, error handling, and CI/CD support.

**Architecture:** Refactor from click-driven to state-driven architecture with URL/DOM fingerprinting. Add selector abstraction layer with priority system (data-testid → aria-label → role → text). Implement retry mechanisms and headless mode for CI/CD integration.

**Tech Stack:** Python 3.x, Playwright, JSON for state tracking

---

## Task 1: Create State Tracking Module

**Files:**
- Create: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/state_tracker.py`
- Test: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/tests/test_state_tracker.py`

**Step 1: Write the failing test**

Create test file with basic state tracking tests:

```python
import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from state_tracker import StateTracker


def test_state_tracker_initialization():
    tracker = StateTracker()
    assert tracker.visited_urls == set()
    assert tracker.visited_states == set()


def test_url_tracking():
    tracker = StateTracker()
    url = "https://cam.example.com/v3/home"

    # First visit should return False (not visited)
    assert tracker.has_visited_url(url) == False

    # Mark as visited
    tracker.mark_url_visited(url)

    # Second check should return True
    assert tracker.has_visited_url(url) == True


def test_dom_fingerprint_tracking():
    tracker = StateTracker()

    # Create mock DOM state
    dom_state = {
        "buttons": ["New", "Export", "Filter"],
        "inputs": ["search", "date"],
        "url": "https://cam.example.com/v3/home"
    }

    fingerprint = tracker.generate_fingerprint(dom_state)

    # First time should not be visited
    assert tracker.has_visited_state(fingerprint) == False

    # Mark as visited
    tracker.mark_state_visited(fingerprint)

    # Should now be visited
    assert tracker.has_visited_state(fingerprint) == True


def test_fingerprint_consistency():
    tracker = StateTracker()

    state1 = {"buttons": ["A", "B"], "url": "test"}
    state2 = {"buttons": ["A", "B"], "url": "test"}

    fp1 = tracker.generate_fingerprint(state1)
    fp2 = tracker.generate_fingerprint(state2)

    # Same state should generate same fingerprint
    assert fp1 == fp2
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts && python -m pytest tests/test_state_tracker.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'state_tracker'"

**Step 3: Write minimal implementation**

```python
import hashlib
import json
from typing import Dict, Any, Set


class StateTracker:
    """Tracks visited URLs and DOM states to prevent duplicate captures"""

    def __init__(self):
        self.visited_urls: Set[str] = set()
        self.visited_states: Set[str] = set()

    def has_visited_url(self, url: str) -> bool:
        """Check if URL has been visited"""
        return url in self.visited_urls

    def mark_url_visited(self, url: str) -> None:
        """Mark URL as visited"""
        self.visited_urls.add(url)

    def generate_fingerprint(self, dom_state: Dict[str, Any]) -> str:
        """Generate unique fingerprint for DOM state"""
        # Sort keys for consistency
        state_json = json.dumps(dom_state, sort_keys=True)
        return hashlib.md5(state_json.encode()).hexdigest()

    def has_visited_state(self, fingerprint: str) -> bool:
        """Check if state has been visited"""
        return fingerprint in self.visited_states

    def mark_state_visited(self, fingerprint: str) -> None:
        """Mark state as visited"""
        self.visited_states.add(fingerprint)
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts && python -m pytest tests/test_state_tracker.py -v`
Expected: PASS (all tests green)

**Step 5: Commit**

```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer
git add scripts/state_tracker.py scripts/tests/test_state_tracker.py
git commit -m "feat: add state tracking module for duplicate detection"
```

---

## Task 2: Create Selector Abstraction Layer

**Files:**
- Create: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/selector_engine.py`
- Test: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/tests/test_selector_engine.py`

**Step 1: Write the failing test**

```python
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from selector_engine import SelectorEngine, SelectorPriority


def test_selector_priority_enum():
    assert SelectorPriority.DATA_TESTID.value == 1
    assert SelectorPriority.ARIA_LABEL.value == 2
    assert SelectorPriority.ROLE.value == 3
    assert SelectorPriority.TEXT.value == 4


def test_build_selector_with_data_testid():
    engine = SelectorEngine()
    selector = engine.build_selector(
        element_type="button",
        data_testid="create-new-btn"
    )
    assert selector == "[data-testid='create-new-btn']"


def test_build_selector_with_aria_label():
    engine = SelectorEngine()
    selector = engine.build_selector(
        element_type="button",
        aria_label="Create New"
    )
    assert selector == "[aria-label='Create New']"


def test_build_selector_with_role():
    engine = SelectorEngine()
    selector = engine.build_selector(
        element_type="button",
        role="button"
    )
    assert selector == "[role='button']"


def test_build_selector_with_text_fallback():
    engine = SelectorEngine()
    selector = engine.build_selector(
        element_type="button",
        text="New"
    )
    assert selector == "button:has-text('New')"


def test_selector_priority_order():
    engine = SelectorEngine()

    # When multiple attributes provided, should use highest priority
    selector = engine.build_selector(
        element_type="button",
        data_testid="btn-new",
        aria_label="Create",
        text="New"
    )

    # Should prefer data-testid over others
    assert selector == "[data-testid='btn-new']"


def test_get_fallback_selectors():
    engine = SelectorEngine()
    selectors = engine.get_fallback_selectors(
        element_type="button",
        data_testid="btn-new",
        aria_label="Create",
        text="New"
    )

    # Should return list in priority order
    assert len(selectors) == 3
    assert selectors[0] == "[data-testid='btn-new']"
    assert selectors[1] == "[aria-label='Create']"
    assert selectors[2] == "button:has-text('New')"
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts && python -m pytest tests/test_selector_engine.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'selector_engine'"

**Step 3: Write minimal implementation**

```python
from enum import Enum
from typing import Optional, List


class SelectorPriority(Enum):
    """Priority order for selector strategies"""
    DATA_TESTID = 1
    ARIA_LABEL = 2
    ROLE = 3
    TEXT = 4


class SelectorEngine:
    """Builds robust selectors with fallback strategies"""

    def build_selector(
        self,
        element_type: str,
        data_testid: Optional[str] = None,
        aria_label: Optional[str] = None,
        role: Optional[str] = None,
        text: Optional[str] = None
    ) -> str:
        """Build selector using highest priority available attribute"""

        if data_testid:
            return f"[data-testid='{data_testid}']"

        if aria_label:
            return f"[aria-label='{aria_label}']"

        if role:
            return f"[role='{role}']"

        if text:
            return f"{element_type}:has-text('{text}')"

        # Fallback to element type only
        return element_type

    def get_fallback_selectors(
        self,
        element_type: str,
        data_testid: Optional[str] = None,
        aria_label: Optional[str] = None,
        role: Optional[str] = None,
        text: Optional[str] = None
    ) -> List[str]:
        """Get list of selectors in priority order for fallback"""
        selectors = []

        if data_testid:
            selectors.append(f"[data-testid='{data_testid}']")

        if aria_label:
            selectors.append(f"[aria-label='{aria_label}']")

        if role:
            selectors.append(f"[role='{role}']")

        if text:
            selectors.append(f"{element_type}:has-text('{text}')")

        return selectors
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts && python -m pytest tests/test_selector_engine.py -v`
Expected: PASS (all tests green)

**Step 5: Commit**

```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer
git add scripts/selector_engine.py scripts/tests/test_selector_engine.py
git commit -m "feat: add selector abstraction layer with priority system"
```

---

## Task 3: Create Retry Mechanism Module

**Files:**
- Create: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/retry_handler.py`
- Test: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/tests/test_retry_handler.py`

**Step 1: Write the failing test**

```python
import pytest
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from retry_handler import RetryHandler, RetryableError


def test_retry_handler_initialization():
    handler = RetryHandler(max_retries=3, base_delay=0.1)
    assert handler.max_retries == 3
    assert handler.base_delay == 0.1


def test_successful_operation_no_retry():
    handler = RetryHandler(max_retries=3, base_delay=0.1)
    call_count = 0

    def successful_operation():
        nonlocal call_count
        call_count += 1
        return "success"

    result = handler.execute(successful_operation)
    assert result == "success"
    assert call_count == 1


def test_retry_on_retryable_error():
    handler = RetryHandler(max_retries=3, base_delay=0.1)
    call_count = 0

    def failing_then_success():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RetryableError("Temporary failure")
        return "success"

    result = handler.execute(failing_then_success)
    assert result == "success"
    assert call_count == 3


def test_max_retries_exceeded():
    handler = RetryHandler(max_retries=2, base_delay=0.1)
    call_count = 0

    def always_fails():
        nonlocal call_count
        call_count += 1
        raise RetryableError("Always fails")

    with pytest.raises(RetryableError):
        handler.execute(always_fails)

    assert call_count == 3
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts && python -m pytest tests/test_retry_handler.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'retry_handler'"

**Step 3: Write minimal implementation**

```python
import time
import logging
from typing import Callable, TypeVar

T = TypeVar('T')
logger = logging.getLogger(__name__)


class RetryableError(Exception):
    """Exception that indicates operation should be retried"""
    pass


class RetryHandler:
    """Handles retry logic with exponential backoff"""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    def execute(self, operation: Callable[[], T]) -> T:
        """Execute operation with retry logic"""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return operation()
            except RetryableError as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"Max retries ({self.max_retries}) exceeded")

        raise last_exception
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts && python -m pytest tests/test_retry_handler.py -v`
Expected: PASS (all tests green)

**Step 5: Commit**

```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer
git add scripts/retry_handler.py scripts/tests/test_retry_handler.py
git commit -m "feat: add retry mechanism with exponential backoff"
```

---

## Task 4: Upgrade auto_login_cam to V3

**Files:**
- Create: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/auto_login_cam_v3.py`

**Step 1: Copy and modify v2 to v3**

```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts
cp auto_login_cam_v2.py auto_login_cam_v3.py
```

**Step 2: Add headless mode and retry support**

Key changes to make in auto_login_cam_v3.py:

1. Add imports:
```python
from retry_handler import RetryHandler, RetryableError
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

2. Add headless parameter to auto_login function
3. Update browser launch to use headless parameter
4. Fix URL inconsistency (default should match docstring)
5. Improve login success validation (check for error messages, not just URL)
6. Wrap login in retry handler
7. Add --headless CLI argument

**Step 3: Test manually**

Run: `python auto_login_cam_v3.py --username admin --password test --headless`

**Step 4: Commit**

```bash
git add scripts/auto_login_cam_v3.py
git commit -m "feat: add auto_login_cam v3 with headless mode and retry"
```

---

## Task 5: Upgrade auto_browse_cam to V3 - State Tracking

**Files:**
- Create: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/auto_browse_cam_v3.py`

**Step 1: Copy v2 to v3**

```bash
cp auto_browse_cam_v2.py auto_browse_cam_v3.py
```

**Step 2: Integrate state tracking**

Add to __init__:
```python
self.state_tracker = StateTracker()
self.selector_engine = SelectorEngine()
self.retry_handler = RetryHandler(max_retries=2, base_delay=1.0)
self.headless = headless
```

Add state change detection method:
```python
def _detect_state_change(self, previous_url: str) -> bool:
    current_url = self.page.url
    if current_url != previous_url:
        return True

    dom_state = {
        "url": current_url,
        "buttons": [btn.text_content().strip() for btn in self.page.locator("button:visible").all()[:20]],
        "dialogs": self.page.locator("[role='dialog']:visible").count()
    }

    fingerprint = self.state_tracker.generate_fingerprint(dom_state)
    if self.state_tracker.has_visited_state(fingerprint):
        return False

    self.state_tracker.mark_state_visited(fingerprint)
    return True
```

**Step 3: Update capture_screenshot to skip duplicates**

**Step 4: Commit**

```bash
git add scripts/auto_browse_cam_v3.py
git commit -m "feat: add state tracking to auto_browse_cam v3"
```

---

## Task 6: Upgrade auto_browse_cam V3 - Selector Engine Integration

**Files:**
- Modify: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/auto_browse_cam_v3.py`

**Step 1: Replace text-based selectors with selector engine**

Find all instances of text-based selectors and replace with selector engine calls.

Example - Replace line 179:
```python
# OLD:
new_buttons = self.page.locator("button:has-text('New'):visible").all()

# NEW:
new_button_selectors = self.selector_engine.get_fallback_selectors(
    element_type="button",
    aria_label="New",
    text="New"
)
new_buttons = []
for selector in new_button_selectors:
    try:
        buttons = self.page.locator(f"{selector}:visible").all()
        if buttons:
            new_buttons = buttons
            break
    except:
        continue
```

**Step 2: Update _capture_interactive_elements to use selector engine**

Replace hardcoded selectors (lines 212-240) with selector engine patterns.

**Step 3: Add logging for selector fallback**

When a selector fails and fallback is used, log it:
```python
logger.info(f"Primary selector failed, using fallback: {selector}")
```

**Step 4: Commit**

```bash
git add scripts/auto_browse_cam_v3.py
git commit -m "feat: integrate selector engine with fallback strategies"
```

---

## Task 7: Add Error Handling and Logging

**Files:**
- Modify: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/auto_browse_cam_v3.py`

**Step 1: Replace bare except blocks**

Find all `except:` blocks and replace with specific exceptions:

```python
# OLD:
except:
    continue

# NEW:
except (PlaywrightTimeout, Exception) as e:
    logger.warning(f"Failed to interact with element: {e}")
    continue
```

**Step 2: Add structured logging**

Replace print statements with logger calls:
```python
# OLD:
print(f"Found {len(elements)} {element_type}(s)")

# NEW:
logger.info(f"Found {len(elements)} {element_type}(s)")
```

**Step 3: Add error context**

When catching exceptions, include context:
```python
except Exception as e:
    logger.error(f"Failed to capture {step_name}: {e}", exc_info=True)
```

**Step 4: Commit**

```bash
git add scripts/auto_browse_cam_v3.py
git commit -m "feat: improve error handling and logging"
```

---

## Task 8: Add Headless Mode and CLI Arguments

**Files:**
- Modify: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/auto_browse_cam_v3.py`

**Step 1: Add headless parameter to main()**

```python
parser.add_argument(
    '--headless',
    action='store_true',
    help='Run in headless mode (no browser window)'
)
```

**Step 2: Pass headless to CAMCaptureV3**

```python
capture = CAMCaptureV3(
    auth_file=args.auth_file,
    output_dir=args.output,
    headless=args.headless
)
```

**Step 3: Update launch_browser to use headless**

```python
self.browser = self.playwright.chromium.launch(
    headless=self.headless,
    channel="chrome" if not self.headless else None,
    proxy={"server": "http://localhost:7890"}
)
```

**Step 4: Test headless mode**

Run: `python auto_browse_cam_v3.py --url https://cam.camrealtest.top/v3/home --feature-name test --headless`

**Step 5: Commit**

```bash
git add scripts/auto_browse_cam_v3.py
git commit -m "feat: add headless mode support for CI/CD"
```

---

## Task 9: Create Integration Tests

**Files:**
- Create: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts/tests/test_integration_v3.py`

**Step 1: Write integration test**

```python
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auto_browse_cam_v3 import CAMCaptureV3


@pytest.mark.integration
def test_state_tracker_prevents_duplicates():
    """Test that state tracker prevents duplicate captures"""
    capture = CAMCaptureV3(headless=True)
    capture.state_tracker.mark_url_visited("https://test.com")

    assert capture.state_tracker.has_visited_url("https://test.com") == True
    assert capture.state_tracker.has_visited_url("https://other.com") == False


@pytest.mark.integration
def test_selector_engine_fallback():
    """Test that selector engine provides fallback selectors"""
    capture = CAMCaptureV3(headless=True)
    selectors = capture.selector_engine.get_fallback_selectors(
        element_type="button",
        data_testid="btn-new",
        text="New"
    )

    assert len(selectors) >= 2
    assert "[data-testid='btn-new']" in selectors
```

**Step 2: Run integration tests**

Run: `cd /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts && python -m pytest tests/test_integration_v3.py -v -m integration`

**Step 3: Commit**

```bash
git add scripts/tests/test_integration_v3.py
git commit -m "test: add integration tests for v3 features"
```

---

## Task 10: Update Documentation

**Files:**
- Modify: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/AUTO_CAPTURE_GUIDE.md`
- Modify: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/CHANGELOG.md`
- Modify: `/Users/jessiecao/.claude/skills/cam-user-guide-writer/skill.md`

**Step 1: Update AUTO_CAPTURE_GUIDE.md**

Add V3 section:
```markdown
## V3 Improvements (March 2026)

### New Features
- **State-driven capture**: Detects URL and DOM changes to prevent duplicate captures
- **Selector abstraction**: Priority system (data-testid → aria-label → role → text)
- **Retry mechanism**: Exponential backoff for transient failures
- **Headless mode**: CI/CD compatible with `--headless` flag
- **Improved error handling**: Specific exceptions with context logging

### Usage
```bash
# Login with headless mode
python auto_login_cam_v3.py --username admin --password pwd --headless

# Capture with headless mode
python auto_browse_cam_v3.py --url <url> --feature-name <name> --headless
```
```

**Step 2: Update CHANGELOG.md**

Add v3.0 entry:
```markdown
## [3.0.0] - 2026-03-03

### Added
- State tracking module to prevent duplicate captures
- Selector abstraction layer with priority fallback system
- Retry mechanism with exponential backoff
- Headless mode for CI/CD integration
- Comprehensive error handling and logging

### Changed
- Refactored from click-driven to state-driven architecture
- Replaced text-based selectors with robust selector engine
- Improved login validation logic

### Fixed
- URL inconsistency between docstring and default argument
- Swallowed exceptions now properly logged
- Login success validation now checks for error messages
```

**Step 3: Update skill.md**

Update references from v2 to v3:
- Change all `auto_browse_cam_v2.py` to `auto_browse_cam_v3.py`
- Change all `auto_login_cam_v2.py` to `auto_login_cam_v3.py`
- Add note about headless mode option

**Step 4: Commit**

```bash
git add AUTO_CAPTURE_GUIDE.md CHANGELOG.md skill.md
git commit -m "docs: update documentation for v3 release"
```

---

## Task 11: Archive V2 Scripts

**Files:**
- Move: v2 scripts to archive

**Step 1: Move v2 scripts to archive**

```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts
mkdir -p archive/v2-scripts
mv auto_login_cam_v2.py archive/v2-scripts/
mv auto_browse_cam_v2.py archive/v2-scripts/
```

**Step 2: Update archive README**

Add to `/Users/jessiecao/.claude/skills/cam-user-guide-writer/archive/README.md`:
```markdown
## v2-scripts/ (Superseded by V3 - March 2026)

V2 scripts archived after V3 release with state-driven architecture.

**Superseded by:**
- `auto_login_cam_v3.py` - Adds headless mode, retry, improved validation
- `auto_browse_cam_v3.py` - Adds state tracking, selector engine, error handling

**Why archived:**
- Click-driven architecture prone to duplicates
- Text-based selectors fragile to i18n changes
- Bare exception handling swallowed errors
- No CI/CD support (fixed headless=False)
```

**Step 3: Commit**

```bash
git add archive/
git commit -m "chore: archive v2 scripts after v3 release"
```

---

## Execution Complete

All v3 improvements implemented:
1. ✅ State-driven capture mechanism
2. ✅ Selector abstraction layer
3. ✅ Robust error handling
4. ✅ CI/CD compatibility (headless mode)

**Next Steps:**
1. Run full test suite: `pytest scripts/tests/ -v`
2. Test v3 scripts manually with real CAM instance
3. Update skill package and increment version to 3.0.0
4. Deploy to production
