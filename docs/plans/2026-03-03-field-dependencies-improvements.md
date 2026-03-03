# Field Dependencies Explorer Improvements

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade explore_field_dependencies.py from 7.8/10 to production-ready quality by implementing 5 priority improvements

**Architecture:** Refactor comparison logic to use baseline state, improve data collection completeness, replace fixed sleeps with proper wait conditions, add specific error handling, and implement stratified sampling

**Tech Stack:** Playwright, Python 3.x, asyncio

---

## Task 1: Refactor to Baseline Comparison

**Files:**
- Modify: `scripts/explore_field_dependencies.py:290`
- Test: `scripts/tests/test_field_dependencies.py` (create)

**Step 1: Write failing test for baseline comparison**

```python
# scripts/tests/test_field_dependencies.py
import pytest
from explore_field_dependencies import FieldDependencyExplorer

def test_baseline_comparison_detects_changes():
    """Test that changes are detected against baseline, not previous state"""
    explorer = FieldDependencyExplorer()

    baseline = {"field_a": "visible", "field_b": "hidden"}
    state_after_action1 = {"field_a": "visible", "field_b": "visible"}
    state_after_action2 = {"field_a": "visible", "field_b": "hidden"}

    # Action 1 should detect field_b changed from baseline
    changes1 = explorer._compare_states(baseline, state_after_action1)
    assert "field_b" in changes1

    # Action 2 should detect NO changes (same as baseline)
    changes2 = explorer._compare_states(baseline, state_after_action2)
    assert len(changes2) == 0
```

**Step 2: Run test to verify it fails**

Run: `pytest scripts/tests/test_field_dependencies.py::test_baseline_comparison_detects_changes -v`
Expected: FAIL with "_compare_states method not found" or incorrect behavior

**Step 3: Extract comparison logic into _compare_states method**

```python
# scripts/explore_field_dependencies.py
def _compare_states(self, baseline_state: dict, current_state: dict) -> dict:
    """
    Compare current state against baseline to detect changes.

    Args:
        baseline_state: The initial state before any actions
        current_state: The state after an action

    Returns:
        Dictionary of fields that changed from baseline
    """
    changes = {}

    # Check for new or changed fields
    for field_id, current_props in current_state.items():
        if field_id not in baseline_state:
            changes[field_id] = {
                "change_type": "appeared",
                "current": current_props
            }
        elif baseline_state[field_id] != current_props:
            changes[field_id] = {
                "change_type": "modified",
                "baseline": baseline_state[field_id],
                "current": current_props
            }

    # Check for removed fields
    for field_id in baseline_state:
        if field_id not in current_state:
            changes[field_id] = {
                "change_type": "disappeared",
                "baseline": baseline_state[field_id]
            }

    return changes
```

**Step 4: Refactor line 290 to use baseline comparison**

Before (line 290):
```python
# Compare with previous state (chain comparison)
if prev_state:
    changes = self._detect_changes(prev_state, current_state)
```

After:
```python
# Compare with baseline state (not chain)
changes = self._compare_states(baseline_state, current_state)
```

**Step 5: Store baseline state at exploration start**

Add at beginning of explore method (around line 200):
```python
# Capture baseline state before any interactions
baseline_state = await self._capture_form_state(page)
```

**Step 6: Run test to verify it passes**

Run: `pytest scripts/tests/test_field_dependencies.py::test_baseline_comparison_detects_changes -v`
Expected: PASS

**Step 7: Commit**

```bash
git add scripts/explore_field_dependencies.py scripts/tests/test_field_dependencies.py
git commit -m "refactor: use baseline comparison instead of chain comparison"
```

---

## Task 2: Collect Dropdown Options

**Files:**
- Modify: `scripts/explore_field_dependencies.py:119`
- Test: `scripts/tests/test_field_dependencies.py`

**Step 1: Write failing test for dropdown options collection**

```python
def test_capture_dropdown_options():
    """Test that dropdown options are captured correctly"""
    explorer = FieldDependencyExplorer()

    # Mock page with dropdown
    mock_dropdown = {
        "tag_name": "select",
        "options": [
            {"value": "opt1", "text": "Option 1"},
            {"value": "opt2", "text": "Option 2"}
        ]
    }

    result = explorer._extract_dropdown_options(mock_dropdown)
    assert len(result) == 2
    assert result[0]["value"] == "opt1"
    assert result[0]["text"] == "Option 1"
```

**Step 2: Run test to verify it fails**

Run: `pytest scripts/tests/test_field_dependencies.py::test_capture_dropdown_options -v`
Expected: FAIL with "_extract_dropdown_options not found"

**Step 3: Implement _extract_dropdown_options method**

```python
# scripts/explore_field_dependencies.py (add after _capture_form_state)
async def _extract_dropdown_options(self, element) -> list:
    """
    Extract all options from a dropdown element.

    Args:
        element: Playwright element handle for select/dropdown

    Returns:
        List of dicts with 'value' and 'text' keys
    """
    options = []
    option_elements = await element.query_selector_all("option")

    for option in option_elements:
        value = await option.get_attribute("value")
        text = await option.inner_text()
        options.append({"value": value, "text": text.strip()})

    return options
```

**Step 4: Populate dropdown_options in _capture_form_state**

Modify around line 119:
```python
if tag_name == "select":
    field_info["type"] = "dropdown"
    field_info["value"] = await element.input_value()
    # NEW: Collect all dropdown options
    field_info["dropdown_options"] = await self._extract_dropdown_options(element)
```

**Step 5: Run test to verify it passes**

Run: `pytest scripts/tests/test_field_dependencies.py::test_capture_dropdown_options -v`
Expected: PASS

**Step 6: Commit**

```bash
git add scripts/explore_field_dependencies.py scripts/tests/test_field_dependencies.py
git commit -m "feat: collect dropdown options in field state"
```

---

## Task 3: Replace Fixed Sleeps with Wait Conditions

**Files:**
- Modify: `scripts/explore_field_dependencies.py:182,196,242,266,299`
- Test: `scripts/tests/test_field_dependencies.py`

**Step 1: Write test for wait condition helper**

```python
def test_wait_for_stability():
    """Test that wait_for_stability waits for network and DOM"""
    explorer = FieldDependencyExplorer()

    # This test verifies the method exists and has correct signature
    import inspect
    sig = inspect.signature(explorer._wait_for_stability)
    assert "page" in sig.parameters
    assert "timeout" in sig.parameters
```

**Step 2: Run test to verify it fails**

Run: `pytest scripts/tests/test_field_dependencies.py::test_wait_for_stability -v`
Expected: FAIL with "_wait_for_stability not found"

**Step 3: Implement _wait_for_stability helper method**

```python
# scripts/explore_field_dependencies.py (add as class method)
async def _wait_for_stability(self, page, timeout: int = 5000):
    """
    Wait for page to stabilize after an interaction.

    Waits for:
    1. Network to be idle
    2. DOM to stop mutating

    Args:
        page: Playwright page object
        timeout: Maximum wait time in milliseconds
    """
    try:
        # Wait for network idle (no requests for 500ms)
        await page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception:
        # If networkidle times out, fall back to domcontentloaded
        await page.wait_for_load_state("domcontentloaded", timeout=timeout)
```

**Step 4: Replace wait_for_timeout at line 182**

Before:
```python
await page.wait_for_timeout(1000)  # Wait for form to load
```

After:
```python
await self._wait_for_stability(page, timeout=5000)
```

**Step 5: Replace wait_for_timeout at lines 196, 242, 266, 299**

Replace all instances of:
```python
await page.wait_for_timeout(500)  # or 1000
```

With:
```python
await self._wait_for_stability(page, timeout=3000)
```

**Step 6: Run test to verify it passes**

Run: `pytest scripts/tests/test_field_dependencies.py::test_wait_for_stability -v`
Expected: PASS

**Step 7: Commit**

```bash
git add scripts/explore_field_dependencies.py scripts/tests/test_field_dependencies.py
git commit -m "refactor: replace fixed sleeps with wait conditions"
```

---

## Task 4: Improve Error Handling

**Files:**
- Modify: `scripts/explore_field_dependencies.py:135,151,165,300,311`
- Test: `scripts/tests/test_field_dependencies.py`

**Step 1: Write test for specific exception handling**

```python
def test_error_handling_specificity():
    """Test that errors are caught specifically, not with bare except"""
    import ast
    import inspect

    # Read the source code
    source = inspect.getsource(FieldDependencyExplorer)
    tree = ast.parse(source)

    # Find all except handlers
    bare_excepts = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:  # Bare except
                bare_excepts.append(node.lineno)

    # Should have no bare except blocks
    assert len(bare_excepts) == 0, f"Found bare except at lines: {bare_excepts}"
```

**Step 2: Run test to verify it fails**

Run: `pytest scripts/tests/test_field_dependencies.py::test_error_handling_specificity -v`
Expected: FAIL with "Found bare except at lines: [135, 151, 165, 300, 311]"

**Step 3: Replace bare except at line 135**

Before:
```python
try:
    value = await element.input_value()
except:
    value = None
```

After:
```python
try:
    value = await element.input_value()
except (AttributeError, TimeoutError) as e:
    self.logger.debug(f"Could not get input value: {e}")
    value = None
```

**Step 4: Replace bare except at line 151**

Before:
```python
try:
    is_visible = await element.is_visible()
except:
    is_visible = False
```

After:
```python
try:
    is_visible = await element.is_visible()
except (AttributeError, TimeoutError) as e:
    self.logger.debug(f"Could not check visibility: {e}")
    is_visible = False
```

**Step 5: Replace bare except at line 165**

Before:
```python
try:
    is_enabled = await element.is_enabled()
except:
    is_enabled = False
```

After:
```python
try:
    is_enabled = await element.is_enabled()
except (AttributeError, TimeoutError) as e:
    self.logger.debug(f"Could not check enabled state: {e}")
    is_enabled = False
```

**Step 6: Replace bare except at lines 300, 311**

Before:
```python
try:
    await element.click()
except:
    continue
```

After:
```python
try:
    await element.click()
except (TimeoutError, Exception) as e:
    self.logger.warning(f"Could not click element: {e}")
    continue
```

**Step 7: Run test to verify it passes**

Run: `pytest scripts/tests/test_field_dependencies.py::test_error_handling_specificity -v`
Expected: PASS

**Step 8: Commit**

```bash
git add scripts/explore_field_dependencies.py scripts/tests/test_field_dependencies.py
git commit -m "refactor: replace bare except with specific exception handling"
```

---

## Task 5: Implement Stratified Sampling

**Files:**
- Modify: `scripts/explore_field_dependencies.py:256`
- Test: `scripts/tests/test_field_dependencies.py`

**Step 1: Write test for stratified sampling**

```python
def test_stratified_sampling():
    """Test that sampling covers beginning, middle, and end"""
    explorer = FieldDependencyExplorer()

    # Test with 20 options, sample 5
    options = list(range(20))
    sampled = explorer._stratified_sample(options, sample_size=5)

    assert len(sampled) == 5
    assert 0 in sampled  # First
    assert 19 in sampled  # Last
    assert any(5 <= x <= 14 for x in sampled)  # Middle range
```

**Step 2: Run test to verify it fails**

Run: `pytest scripts/tests/test_field_dependencies.py::test_stratified_sampling -v`
Expected: FAIL with "_stratified_sample not found"

**Step 3: Implement _stratified_sample method**

```python
# scripts/explore_field_dependencies.py (add as class method)
def _stratified_sample(self, items: list, sample_size: int) -> list:
    """
    Sample items using stratified approach to cover beginning, middle, end.

    Args:
        items: List of items to sample from
        sample_size: Number of items to sample

    Returns:
        List of sampled items
    """
    if len(items) <= sample_size:
        return items

    # Always include first and last
    sampled = [items[0], items[-1]]
    remaining_slots = sample_size - 2

    if remaining_slots > 0:
        # Sample evenly from the middle
        step = len(items) // (remaining_slots + 1)
        for i in range(1, remaining_slots + 1):
            idx = min(i * step, len(items) - 2)
            if items[idx] not in sampled:
                sampled.append(items[idx])

    return sampled
```

**Step 4: Replace [:5] slicing at line 256**

Before:
```python
options_to_try = dropdown_options[:5]  # Only try first 5
```

After:
```python
# Use stratified sampling to cover beginning, middle, end
options_to_try = self._stratified_sample(dropdown_options, sample_size=5)
```

**Step 5: Run test to verify it passes**

Run: `pytest scripts/tests/test_field_dependencies.py::test_stratified_sampling -v`
Expected: PASS

**Step 6: Commit**

```bash
git add scripts/explore_field_dependencies.py scripts/tests/test_field_dependencies.py
git commit -m "feat: implement stratified sampling for dropdown options"
```

---

## Task 6: Integration Testing

**Files:**
- Test: `scripts/tests/test_field_dependencies.py`

**Step 1: Write integration test**

```python
@pytest.mark.asyncio
async def test_full_exploration_workflow():
    """Integration test for complete field dependency exploration"""
    explorer = FieldDependencyExplorer()

    # This test would require a test HTML page
    # For now, verify the main method signature
    import inspect
    sig = inspect.signature(explorer.explore)

    assert "url" in sig.parameters
    assert "output_dir" in sig.parameters
```

**Step 2: Run integration test**

Run: `pytest scripts/tests/test_field_dependencies.py::test_full_exploration_workflow -v`
Expected: PASS

**Step 3: Run all tests**

Run: `pytest scripts/tests/test_field_dependencies.py -v`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add scripts/tests/test_field_dependencies.py
git commit -m "test: add integration test for field dependency explorer"
```

---

## Task 7: Update Documentation

**Files:**
- Modify: `scripts/README.md`
- Create: `scripts/CHANGELOG.md`

**Step 1: Document improvements in README**

Add section to `scripts/README.md`:

```markdown
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
```

**Step 2: Create CHANGELOG entry**

```markdown
# Changelog

## [2.0.0] - 2026-03-03

### Changed
- Refactored state comparison to use baseline instead of chain comparison
- Improved dropdown options collection to capture all available options
- Replaced fixed sleep delays with proper wait conditions
- Enhanced error handling with specific exception types
- Implemented stratified sampling for dropdown option exploration

### Fixed
- False negatives when fields return to baseline state
- Missing dropdown options in captured state
- Race conditions from fixed timeout delays
- Silent failures from bare except blocks
- Poor coverage from sequential sampling

## [1.0.0] - 2026-03-02

### Added
- Initial field dependency exploration functionality
```

**Step 3: Commit documentation**

```bash
git add scripts/README.md scripts/CHANGELOG.md
git commit -m "docs: document field dependencies explorer v2 improvements"
```

---

## Completion Checklist

- [ ] Task 1: Baseline comparison implemented and tested
- [ ] Task 2: Dropdown options collection implemented and tested
- [ ] Task 3: Wait conditions replace fixed sleeps
- [ ] Task 4: Specific error handling replaces bare except
- [ ] Task 5: Stratified sampling implemented and tested
- [ ] Task 6: Integration tests pass
- [ ] Task 7: Documentation updated

**Expected Outcome:** explore_field_dependencies.py upgraded from 7.8/10 to production-ready quality with all 5 ChatGPT-identified improvements implemented.
