# Field Dependencies Explorer V3 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade explore_field_dependencies.py from v2 to v3 by adding structured state changes, global exploration budget control, and login strong signal validation

**Architecture:** Add semantic change type classification, implement hard limits for exploration (steps/states/time/retries), and enhance login validation with stable selectors or API verification

**Tech Stack:** Python 3.x, Playwright, enum for change types, dataclass for budget configuration

---

## Task 1: Add Structured State Change Types

**Files:**
- Modify: `scripts/explore_field_dependencies.py:1-30` (add imports and enums)
- Modify: `scripts/explore_field_dependencies.py:230-293` (update _compare_states method)
- Test: `scripts/tests/test_field_dependencies.py`

**Step 1: Write failing test for semantic change types**

```python
# scripts/tests/test_field_dependencies.py
from explore_field_dependencies import FieldDependencyExplorer, ChangeType

def test_classify_change_type_url_change():
    """Test that URL changes are correctly classified"""
    explorer = FieldDependencyExplorer()

    baseline = {"url": "https://example.com/page1"}
    current = {"url": "https://example.com/page2"}

    changes = explorer._compare_states(baseline, current)
    assert changes["url"]["change_type"] == ChangeType.URL_CHANGE.value

def test_classify_change_type_dialog_opened():
    """Test that dialog opening is correctly classified"""
    explorer = FieldDependencyExplorer()

    baseline = {"visible_fields": ["field1"]}
    current = {"visible_fields": ["field1", "dialog_title", "dialog_content"]}

    changes = explorer._compare_states(baseline, current)
    # Dialog detected when multiple fields appear with "dialog" in aria-label
    assert any(ChangeType.DIALOG_OPENED.value in str(change)
               for change in changes.values())

def test_classify_change_type_field_added():
    """Test that field additions are correctly classified"""
    explorer = FieldDependencyExplorer()

    baseline = {"field_a": {"visible": True}}
    current = {"field_a": {"visible": True}, "field_b": {"visible": True}}

    changes = explorer._compare_states(baseline, current)
    assert changes["field_b"]["change_type"] == ChangeType.FIELD_ADDED.value

def test_classify_change_type_options_changed():
    """Test that dropdown option changes are correctly classified"""
    explorer = FieldDependencyExplorer()

    baseline = {"dropdown": {"options": ["A", "B"]}}
    current = {"dropdown": {"options": ["A", "B", "C"]}}

    changes = explorer._compare_states(baseline, current)
    assert changes["dropdown"]["change_type"] == ChangeType.OPTIONS_CHANGED.value
```

**Step 2: Run test to verify it fails**

Run: `pytest scripts/tests/test_field_dependencies.py::test_classify_change_type_url_change -v`
Expected: FAIL with "ChangeType not found" or "change_type key missing"

**Step 3: Add ChangeType enum**

```python
# scripts/explore_field_dependencies.py (add after imports, around line 28)
from enum import Enum

class ChangeType(Enum):
    """Semantic types of state changes for better interpretability"""
    URL_CHANGE = "url_change"
    DIALOG_OPENED = "dialog_opened"
    DIALOG_CLOSED = "dialog_closed"
    FIELD_ADDED = "field_added"
    FIELD_REMOVED = "field_removed"
    FIELD_MODIFIED = "field_modified"
    OPTIONS_CHANGED = "options_changed"
    VALIDATION_ERROR = "validation_error"
```

**Step 4: Update _compare_states to classify change types**

```python
# scripts/explore_field_dependencies.py (replace _compare_states method, around line 230)
def _compare_states(self, baseline_state: dict, current_state: dict) -> dict:
    """
    Compare current state against baseline to detect changes with semantic types.

    Args:
        baseline_state: The initial state before any actions
        current_state: The state after an action

    Returns:
        Dictionary of fields that changed from baseline with semantic change_type
    """
    changes = {}

    # Check for URL change
    if baseline_state.get("url") != current_state.get("url"):
        changes["url"] = {
            "change_type": ChangeType.URL_CHANGE.value,
            "baseline": baseline_state.get("url"),
            "current": current_state.get("url")
        }

    # Check for new or changed fields
    for field_id, current_props in current_state.items():
        if field_id == "url":
            continue  # Already handled

        if field_id not in baseline_state:
            # Classify as dialog opened if multiple fields with "dialog" appear
            if self._is_dialog_field(field_id, current_state):
                change_type = ChangeType.DIALOG_OPENED.value
            else:
                change_type = ChangeType.FIELD_ADDED.value

            changes[field_id] = {
                "change_type": change_type,
                "current": current_props
            }
        elif baseline_state[field_id] != current_props:
            # Determine if it's options change or field modification
            if self._is_options_change(baseline_state[field_id], current_props):
                change_type = ChangeType.OPTIONS_CHANGED.value
            elif self._is_validation_error(current_props):
                change_type = ChangeType.VALIDATION_ERROR.value
            else:
                change_type = ChangeType.FIELD_MODIFIED.value

            changes[field_id] = {
                "change_type": change_type,
                "baseline": baseline_state[field_id],
                "current": current_props
            }

    # Check for removed fields
    for field_id in baseline_state:
        if field_id == "url":
            continue

        if field_id not in current_state:
            # Classify as dialog closed if multiple fields with "dialog" disappear
            if self._is_dialog_field(field_id, baseline_state):
                change_type = ChangeType.DIALOG_CLOSED.value
            else:
                change_type = ChangeType.FIELD_REMOVED.value

            changes[field_id] = {
                "change_type": change_type,
                "baseline": baseline_state[field_id]
            }

    return changes
```

**Step 5: Add helper methods for change classification**

```python
# scripts/explore_field_dependencies.py (add after _compare_states)
def _is_dialog_field(self, field_id: str, state: dict) -> bool:
    """Check if field is part of a dialog based on naming patterns"""
    dialog_keywords = ["dialog", "modal", "popup", "overlay"]
    return any(keyword in field_id.lower() for keyword in dialog_keywords)

def _is_options_change(self, baseline_props: dict, current_props: dict) -> bool:
    """Check if change is specifically about dropdown options"""
    return ("options" in baseline_props and "options" in current_props and
            baseline_props.get("options") != current_props.get("options"))

def _is_validation_error(self, props: dict) -> bool:
    """Check if field shows validation error"""
    error_indicators = ["error", "invalid", "required"]
    return any(indicator in str(props).lower() for indicator in error_indicators)
```

**Step 6: Run tests to verify they pass**

Run: `pytest scripts/tests/test_field_dependencies.py -k "test_classify_change_type" -v`
Expected: All 4 new tests PASS

**Step 7: Commit**

```bash
git add scripts/explore_field_dependencies.py scripts/tests/test_field_dependencies.py
git commit -m "feat: add structured state change types with semantic classification"
```

---

## Task 2: Implement Global Exploration Budget Control

**Files:**
- Modify: `scripts/explore_field_dependencies.py:30-46` (add ExplorationBudget class)
- Modify: `scripts/explore_field_dependencies.py:200-400` (add budget checks in explore methods)
- Test: `scripts/tests/test_field_dependencies.py`

**Step 1: Write failing test for budget enforcement**

```python
# scripts/tests/test_field_dependencies.py
from explore_field_dependencies import ExplorationBudget

def test_exploration_budget_max_steps():
    """Test that exploration stops at max_steps"""
    budget = ExplorationBudget(max_steps=5)

    assert budget.can_continue_steps() == True

    for i in range(5):
        budget.increment_steps()

    assert budget.can_continue_steps() == False
    assert budget.steps_taken == 5

def test_exploration_budget_max_states():
    """Test that exploration stops at max_states"""
    budget = ExplorationBudget(max_states=3)

    budget.record_state("state1")
    budget.record_state("state2")
    budget.record_state("state3")

    assert budget.can_continue_states() == False
    assert len(budget.visited_states) == 3

def test_exploration_budget_max_time():
    """Test that exploration stops after max_time"""
    import time
    budget = ExplorationBudget(max_time_seconds=1)

    assert budget.can_continue_time() == True
    time.sleep(1.1)
    assert budget.can_continue_time() == False

def test_exploration_budget_max_retries():
    """Test that retries are limited per action"""
    budget = ExplorationBudget(max_retries_per_action=3)

    action_id = "click_button"
    assert budget.can_retry(action_id) == True

    for i in range(3):
        budget.increment_retries(action_id)

    assert budget.can_retry(action_id) == False
```

**Step 2: Run test to verify it fails**

Run: `pytest scripts/tests/test_field_dependencies.py::test_exploration_budget_max_steps -v`
Expected: FAIL with "ExplorationBudget not found"

**Step 3: Implement ExplorationBudget class**

```python
# scripts/explore_field_dependencies.py (add after ChangeType enum, around line 40)
from dataclasses import dataclass, field
from time import time

@dataclass
class ExplorationBudget:
    """
    Global budget control to prevent exploration time explosion.

    Provides hard limits on:
    - Total steps taken
    - Unique states visited
    - Total execution time
    - Retries per action
    """
    max_steps: int = 100
    max_states: int = 50
    max_time_seconds: int = 300  # 5 minutes
    max_retries_per_action: int = 3

    # Internal tracking
    steps_taken: int = field(default=0, init=False)
    visited_states: set = field(default_factory=set, init=False)
    retry_counts: dict = field(default_factory=dict, init=False)
    start_time: float = field(default_factory=time, init=False)

    def can_continue_steps(self) -> bool:
        """Check if we can take more steps"""
        return self.steps_taken < self.max_steps

    def can_continue_states(self) -> bool:
        """Check if we can visit more states"""
        return len(self.visited_states) < self.max_states

    def can_continue_time(self) -> bool:
        """Check if we have time remaining"""
        elapsed = time() - self.start_time
        return elapsed < self.max_time_seconds

    def can_continue(self) -> bool:
        """Check if exploration can continue (all budgets)"""
        return (self.can_continue_steps() and
                self.can_continue_states() and
                self.can_continue_time())

    def increment_steps(self):
        """Increment step counter"""
        self.steps_taken += 1

    def record_state(self, state_fingerprint: str):
        """Record a visited state"""
        self.visited_states.add(state_fingerprint)

    def can_retry(self, action_id: str) -> bool:
        """Check if action can be retried"""
        return self.retry_counts.get(action_id, 0) < self.max_retries_per_action

    def increment_retries(self, action_id: str):
        """Increment retry counter for action"""
        self.retry_counts[action_id] = self.retry_counts.get(action_id, 0) + 1

    def get_status(self) -> dict:
        """Get current budget status"""
        elapsed = time() - self.start_time
        return {
            "steps": f"{self.steps_taken}/{self.max_steps}",
            "states": f"{len(self.visited_states)}/{self.max_states}",
            "time": f"{elapsed:.1f}s/{self.max_time_seconds}s",
            "can_continue": self.can_continue()
        }
```

**Step 4: Add budget to FieldDependencyExplorer __init__**

```python
# scripts/explore_field_dependencies.py (modify __init__, around line 80)
def __init__(self, auth_file=".auth/state.json", output_dir="captured_data",
             budget: ExplorationBudget = None):
    self.auth_file = Path(auth_file)
    self.output_dir = Path(output_dir)
    self.output_dir.mkdir(exist_ok=True)

    self.screenshots_dir = self.output_dir / "screenshots"
    self.screenshots_dir.mkdir(exist_ok=True)

    self.playwright = None
    self.browser = None
    self.context = None
    self.page = None
    self.captured_steps = []
    self.step_counter = 1
    self.field_dependencies = {}

    # Budget control
    self.budget = budget or ExplorationBudget()
```

**Step 5: Add budget checks in _explore_form_fields method**

```python
# scripts/explore_field_dependencies.py (modify _explore_form_fields, around line 340)
def _explore_form_fields(self, page):
    """Explore form field dependencies with budget control"""
    print("\n=== Exploring Form Field Dependencies ===")

    # Capture baseline state before any interactions
    baseline_state = self.extract_form_state()
    state_fingerprint = json.dumps(baseline_state, sort_keys=True)
    self.budget.record_state(state_fingerprint)

    # ... existing code ...

    for field_label, options in dropdown_options.items():
        # Check budget before exploring each field
        if not self.budget.can_continue():
            print(f"\n⚠️  Budget exhausted: {self.budget.get_status()}")
            break

        self.budget.increment_steps()
        print(f"\n--- Testing field: {field_label} (Step {self.budget.steps_taken}) ---")
        print(f"Budget status: {self.budget.get_status()}")

        # ... existing exploration code ...

        # Record state after each interaction
        after_state = self.extract_form_state()
        state_fingerprint = json.dumps(after_state, sort_keys=True)
        self.budget.record_state(state_fingerprint)
```

**Step 6: Run tests to verify they pass**

Run: `pytest scripts/tests/test_field_dependencies.py -k "test_exploration_budget" -v`
Expected: All 4 budget tests PASS

**Step 7: Commit**

```bash
git add scripts/explore_field_dependencies.py scripts/tests/test_field_dependencies.py
git commit -m "feat: add global exploration budget control with hard limits"
```

---

## Task 3: Add Login Strong Signal Validation

**Files:**
- Modify: `scripts/auto_login_cam_v3.py:200-250` (enhance login validation)
- Test: `scripts/tests/test_auto_login.py` (create if doesn't exist)

**Step 1: Write failing test for strong signal validation**

```python
# scripts/tests/test_auto_login.py
from auto_login_cam_v3 import LoginValidator

def test_login_validator_home_selector():
    """Test that login validator checks for stable home selector"""
    validator = LoginValidator(
        home_selectors=[".user-menu", "[data-testid='user-profile']"]
    )

    # Mock page with home selector
    class MockPage:
        def locator(self, selector):
            class MockLocator:
                def is_visible(self, timeout=None):
                    return selector == ".user-menu"
            return MockLocator()

    page = MockPage()
    assert validator.verify_login_success(page) == True

def test_login_validator_api_check():
    """Test that login validator can verify via API"""
    validator = LoginValidator(
        api_endpoint="/api/user/info",
        expected_status=200
    )

    # Mock page with API response
    class MockPage:
        def request(self):
            class MockRequest:
                def get(self, url):
                    class MockResponse:
                        status = 200
                    return MockResponse()
            return MockRequest()

    page = MockPage()
    assert validator.verify_login_via_api(page) == True

def test_login_validator_combined():
    """Test that validator uses both selector and API"""
    validator = LoginValidator(
        home_selectors=[".user-menu"],
        api_endpoint="/api/user/info",
        require_both=True
    )

    # Should require both checks to pass
    assert validator.validation_strategy == "combined"
```

**Step 2: Run test to verify it fails**

Run: `pytest scripts/tests/test_auto_login.py::test_login_validator_home_selector -v`
Expected: FAIL with "LoginValidator not found"

**Step 3: Implement LoginValidator class**

```python
# scripts/auto_login_cam_v3.py (add new class)
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class LoginValidator:
    """
    Strong signal validation for login success.

    Provides multiple validation strategies:
    1. Home selector check (wait for stable UI element)
    2. API endpoint check (verify authenticated API call)
    3. Combined (both must pass)
    """
    home_selectors: List[str] = None
    api_endpoint: Optional[str] = None
    expected_status: int = 200
    require_both: bool = False
    timeout: int = 10000  # 10 seconds

    def __post_init__(self):
        if self.home_selectors is None:
            self.home_selectors = [
                ".user-menu",
                "[data-testid='user-profile']",
                ".account-dropdown"
            ]

        if self.require_both and not self.api_endpoint:
            raise ValueError("require_both=True requires api_endpoint to be set")

    @property
    def validation_strategy(self) -> str:
        """Get current validation strategy"""
        if self.require_both:
            return "combined"
        elif self.api_endpoint:
            return "api_primary"
        else:
            return "selector_only"

    def verify_login_success(self, page) -> bool:
        """
        Verify login success using configured strategy.

        Args:
            page: Playwright page object

        Returns:
            True if login verified, False otherwise
        """
        selector_valid = self._check_home_selectors(page)

        if self.api_endpoint:
            api_valid = self.verify_login_via_api(page)

            if self.require_both:
                return selector_valid and api_valid
            else:
                # API check is primary, selector is fallback
                return api_valid or selector_valid

        return selector_valid

    def _check_home_selectors(self, page) -> bool:
        """Check if any home selector is visible"""
        for selector in self.home_selectors:
            try:
                locator = page.locator(selector)
                if locator.is_visible(timeout=self.timeout):
                    print(f"✓ Login verified: found home selector '{selector}'")
                    return True
            except Exception as e:
                print(f"  Selector '{selector}' not found: {e}")
                continue

        print("✗ Login verification failed: no home selectors found")
        return False

    def verify_login_via_api(self, page) -> bool:
        """
        Verify login by calling authenticated API endpoint.

        Args:
            page: Playwright page object

        Returns:
            True if API returns expected status, False otherwise
        """
        try:
            # Make API request using page context (includes cookies)
            response = page.request.get(self.api_endpoint)

            if response.status == self.expected_status:
                print(f"✓ Login verified: API {self.api_endpoint} returned {response.status}")
                return True
            else:
                print(f"✗ API check failed: expected {self.expected_status}, got {response.status}")
                return False

        except Exception as e:
            print(f"✗ API check failed: {e}")
            return False
```

**Step 4: Integrate LoginValidator into auto_login_cam_v3.py**

```python
# scripts/auto_login_cam_v3.py (modify login verification section)
def verify_login(self, page) -> bool:
    """Verify login success with strong signal validation"""
    print("\n=== Verifying Login Success ===")

    # Use LoginValidator for robust verification
    validator = LoginValidator(
        home_selectors=[".user-menu", "[data-testid='user-profile']"],
        api_endpoint="/api/user/info",  # Adjust to actual CAM API
        require_both=False  # API primary, selector fallback
    )

    return validator.verify_login_success(page)
```

**Step 5: Run tests to verify they pass**

Run: `pytest scripts/tests/test_auto_login.py -v`
Expected: All 3 tests PASS

**Step 6: Update documentation**

```markdown
# scripts/README.md (add section)

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
```

**Step 7: Commit**

```bash
git add scripts/auto_login_cam_v3.py scripts/tests/test_auto_login.py scripts/README.md
git commit -m "feat: add login strong signal validation with selector and API checks"
```

---

## Task 4: Integration Testing

**Files:**
- Test: `scripts/tests/test_field_dependencies.py`

**Step 1: Write integration test for v3 features**

```python
# scripts/tests/test_field_dependencies.py
def test_v3_integration():
    """Integration test for v3 features: structured changes + budget + validation"""
    # Test that all v3 components work together
    budget = ExplorationBudget(max_steps=10, max_states=5, max_time_seconds=60)
    explorer = FieldDependencyExplorer(budget=budget)

    # Verify budget is initialized
    assert explorer.budget.max_steps == 10
    assert explorer.budget.can_continue() == True

    # Verify ChangeType enum is available
    assert hasattr(explorer, '_compare_states')
    assert ChangeType.URL_CHANGE.value == "url_change"

    # Verify LoginValidator is available
    from auto_login_cam_v3 import LoginValidator
    validator = LoginValidator()
    assert validator.validation_strategy in ["selector_only", "api_primary", "combined"]
```

**Step 2: Run integration test**

Run: `pytest scripts/tests/test_field_dependencies.py::test_v3_integration -v`
Expected: PASS

**Step 3: Run all tests**

Run: `pytest scripts/tests/ -v`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add scripts/tests/test_field_dependencies.py
git commit -m "test: add v3 integration test"
```

---

## Task 5: Update Documentation

**Files:**
- Modify: `scripts/README.md`
- Modify: `scripts/CHANGELOG.md`

**Step 1: Document v3 improvements in README**

```markdown
# scripts/README.md (add section)

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
```

**Step 2: Update CHANGELOG**

```markdown
# scripts/CHANGELOG.md (add v3 entry)

## [3.0.0] - 2026-03-03

### Added
- Structured state change types with semantic classification (URL change, dialog opened/closed, field added/removed, options changed, validation error)
- Global exploration budget control with hard limits (max steps, states, time, retries)
- Login strong signal validation with home selector and API verification strategies
- ExplorationBudget class for preventing exploration time explosion
- LoginValidator class for robust login verification
- Integration tests for v3 features

### Changed
- `_compare_states()` now returns semantic change types instead of generic "appeared/modified/disappeared"
- Login verification now uses multiple validation strategies (selector + API)
- Exploration loop now checks budget constraints before each interaction

### Improved
- Better interpretability of state changes for LLM-based documentation generation
- More predictable execution time with hard budget limits
- More reliable login verification with fallback strategies

## [2.0.0] - 2026-03-03
...
```

**Step 3: Commit documentation**

```bash
git add scripts/README.md scripts/CHANGELOG.md
git commit -m "docs: document v3 improvements (structured changes, budget, login validation)"
```

---

## Completion Checklist

- [ ] Task 1: Structured state change types implemented and tested
- [ ] Task 2: Global exploration budget control implemented and tested
- [ ] Task 3: Login strong signal validation implemented and tested
- [ ] Task 4: Integration tests pass
- [ ] Task 5: Documentation updated

**Expected Outcome:** explore_field_dependencies.py upgraded to v3 with semantic change classification, hard exploration limits, and robust login validation - addressing all ChatGPT feedback points.
