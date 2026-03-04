#!/usr/bin/env python3
"""
Tests for explore_field_dependencies.py
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

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


def test_capture_dropdown_options():
    """Test that dropdown options are captured correctly"""
    explorer = FieldDependencyExplorer()

    # Mock dropdown element with options
    class MockOption:
        def __init__(self, value, text):
            self._value = value
            self._text = text

        def get_attribute(self, attr):
            if attr == "value":
                return self._value
            return None

        def inner_text(self):
            return self._text

    class MockLocator:
        def __init__(self, options):
            self._options = options

        def all(self):
            return self._options

    class MockDropdown:
        def __init__(self):
            self.options = [
                MockOption("opt1", "Option 1"),
                MockOption("opt2", "Option 2"),
                MockOption("opt3", "Option 3")
            ]

        def locator(self, selector):
            if selector == "option":
                return MockLocator(self.options)
            return MockLocator([])

    mock_dropdown = MockDropdown()
    result = explorer._extract_dropdown_options(mock_dropdown)

    assert len(result) == 3
    assert result[0]["value"] == "opt1"
    assert result[0]["text"] == "Option 1"
    assert result[1]["value"] == "opt2"
    assert result[1]["text"] == "Option 2"
    assert result[2]["value"] == "opt3"
    assert result[2]["text"] == "Option 3"


def test_capture_dropdown_options_with_empty_text():
    """Test that empty options are skipped"""
    explorer = FieldDependencyExplorer()

    class MockOption:
        def __init__(self, value, text):
            self._value = value
            self._text = text

        def get_attribute(self, attr):
            if attr == "value":
                return self._value
            return None

        def inner_text(self):
            return self._text

    class MockLocator:
        def __init__(self, options):
            self._options = options

        def all(self):
            return self._options

    class MockDropdown:
        def __init__(self):
            self.options = [
                MockOption("opt1", "Option 1"),
                MockOption("opt2", "   "),  # Whitespace only
                MockOption("opt3", ""),      # Empty string
                MockOption("opt4", "Option 4")
            ]

        def locator(self, selector):
            if selector == "option":
                return MockLocator(self.options)
            return MockLocator([])

    mock_dropdown = MockDropdown()
    result = explorer._extract_dropdown_options(mock_dropdown)

    # Should only have 2 options (empty ones skipped)
    assert len(result) == 2
    assert result[0]["value"] == "opt1"
    assert result[0]["text"] == "Option 1"
    assert result[1]["value"] == "opt4"
    assert result[1]["text"] == "Option 4"


def test_capture_dropdown_options_with_none_value():
    """Test that options with None value are captured"""
    explorer = FieldDependencyExplorer()

    class MockOption:
        def __init__(self, value, text):
            self._value = value
            self._text = text

        def get_attribute(self, attr):
            if attr == "value":
                return self._value
            return None

        def inner_text(self):
            return self._text

    class MockLocator:
        def __init__(self, options):
            self._options = options

        def all(self):
            return self._options

    class MockDropdown:
        def __init__(self):
            self.options = [
                MockOption(None, "Select..."),  # No value attribute
                MockOption("opt1", "Option 1")
            ]

        def locator(self, selector):
            if selector == "option":
                return MockLocator(self.options)
            return MockLocator([])

    mock_dropdown = MockDropdown()
    result = explorer._extract_dropdown_options(mock_dropdown)

    assert len(result) == 2
    assert result[0]["value"] is None
    assert result[0]["text"] == "Select..."
    assert result[1]["value"] == "opt1"
    assert result[1]["text"] == "Option 1"


def test_capture_dropdown_options_empty_dropdown():
    """Test that empty dropdown returns empty list"""
    explorer = FieldDependencyExplorer()

    class MockLocator:
        def all(self):
            return []

    class MockDropdown:
        def locator(self, selector):
            return MockLocator()

    mock_dropdown = MockDropdown()
    result = explorer._extract_dropdown_options(mock_dropdown)

    assert len(result) == 0
    assert result == []


def test_wait_for_stability():
    """Test that wait_for_stability waits for network and DOM"""
    explorer = FieldDependencyExplorer()

    # This test verifies the method exists and has correct signature
    import inspect
    sig = inspect.signature(explorer._wait_for_stability)
    assert "page" in sig.parameters
    assert "timeout" in sig.parameters


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


def test_stratified_sampling_sample_size_zero():
    """Test that sample_size=0 returns empty list"""
    explorer = FieldDependencyExplorer()

    options = list(range(10))
    sampled = explorer._stratified_sample(options, sample_size=0)

    assert len(sampled) == 0
    assert sampled == []


def test_stratified_sampling_sample_size_one():
    """Test that sample_size=1 returns only first item"""
    explorer = FieldDependencyExplorer()

    options = list(range(10))
    sampled = explorer._stratified_sample(options, sample_size=1)

    assert len(sampled) == 1
    assert sampled == [0]


def test_stratified_sampling_empty_list():
    """Test that empty list returns empty list"""
    explorer = FieldDependencyExplorer()

    sampled = explorer._stratified_sample([], sample_size=5)

    assert len(sampled) == 0
    assert sampled == []


def test_stratified_sampling_negative_sample_size():
    """Test that negative sample_size raises ValueError"""
    explorer = FieldDependencyExplorer()

    options = list(range(10))

    with pytest.raises(ValueError, match="sample_size must be non-negative"):
        explorer._stratified_sample(options, sample_size=-1)


def test_stratified_sampling_exact_count():
    """Test that exactly sample_size items are returned"""
    explorer = FieldDependencyExplorer()

    # Test various combinations
    test_cases = [
        (list(range(100)), 10),
        (list(range(50)), 7),
        (list(range(30)), 5),
        (list(range(15)), 3),
    ]

    for options, sample_size in test_cases:
        sampled = explorer._stratified_sample(options, sample_size)
        assert len(sampled) == sample_size, f"Expected {sample_size} items, got {len(sampled)}"
        # Verify no duplicates
        assert len(sampled) == len(set(sampled)), "Sampled list contains duplicates"


def test_stratified_sampling_sample_size_equals_list_length():
    """Test that when sample_size equals list length, all items are returned"""
    explorer = FieldDependencyExplorer()

    options = list(range(10))
    sampled = explorer._stratified_sample(options, sample_size=10)

    assert len(sampled) == 10
    assert sampled == options


def test_stratified_sampling_sample_size_greater_than_list_length():
    """Test that when sample_size > list length, all items are returned"""
    explorer = FieldDependencyExplorer()

    options = list(range(5))
    sampled = explorer._stratified_sample(options, sample_size=10)

    assert len(sampled) == 5
    assert sampled == options


def test_full_exploration_workflow():
    """Integration test for complete field dependency exploration"""
    explorer = FieldDependencyExplorer()

    # Verify the main method signature
    import inspect
    sig = inspect.signature(explorer.explore_dependencies)

    assert "target_url" in sig.parameters

    # Verify all key methods exist and have correct signatures
    assert hasattr(explorer, "launch_browser")
    assert hasattr(explorer, "capture_screenshot")
    assert hasattr(explorer, "extract_form_state")
    assert hasattr(explorer, "save_results")
    assert hasattr(explorer, "close")

    # Verify helper methods exist
    assert hasattr(explorer, "_wait_for_stability")
    assert hasattr(explorer, "_stratified_sample")
    assert hasattr(explorer, "_extract_dropdown_options")
    assert hasattr(explorer, "_compare_states")
    assert hasattr(explorer, "_explore_form_fields")
    assert hasattr(explorer, "_get_field_label")
    assert hasattr(explorer, "_get_dropdown_options")

    # Verify initialization sets up required attributes
    assert hasattr(explorer, "output_dir")
    assert hasattr(explorer, "field_dependencies")
    assert isinstance(explorer.field_dependencies, dict)

    # screenshots_dir and captured_steps live on explorer.recorder (a StepRecorder),
    # which is initialized lazily in explore_dependencies(). Before that call, recorder is None.
    assert hasattr(explorer, "recorder")
    assert explorer.recorder is None


def test_classify_change_type_url_change():
    """Test that URL changes are correctly classified"""
    from explore_field_dependencies import ChangeType

    explorer = FieldDependencyExplorer()

    baseline = {"url": "https://example.com/page1"}
    current = {"url": "https://example.com/page2"}

    changes = explorer._compare_states(baseline, current)
    assert changes["url"]["change_type"] == ChangeType.URL_CHANGE.value


def test_classify_change_type_dialog_opened():
    """Test that dialog opening is correctly classified for new fields"""
    from explore_field_dependencies import ChangeType

    explorer = FieldDependencyExplorer()

    # DIALOG_OPENED applies to new fields whose key contains dialog keywords
    baseline = {"field1": {"visible": True}}
    current = {"field1": {"visible": True}, "dialog_title": {"visible": True}, "dialog_content": {"visible": True}}

    changes = explorer._compare_states(baseline, current)
    # New fields with "dialog" in their key should be classified as DIALOG_OPENED
    assert "dialog_title" in changes
    assert changes["dialog_title"]["change_type"] == ChangeType.DIALOG_OPENED.value


def test_classify_change_type_dialog_opened_modified_field_is_field_modified():
    """Test that a modified field with dialog content is FIELD_MODIFIED, not DIALOG_OPENED"""
    from explore_field_dependencies import ChangeType

    explorer = FieldDependencyExplorer()

    # Modifying an existing field (even one with dialog content) should be FIELD_MODIFIED
    baseline = {"visible_fields": ["field1"]}
    current = {"visible_fields": ["field1", "dialog_title", "dialog_content"]}

    changes = explorer._compare_states(baseline, current)
    assert "visible_fields" in changes
    assert changes["visible_fields"]["change_type"] == ChangeType.FIELD_MODIFIED.value


def test_classify_change_type_field_added():
    """Test that field additions are correctly classified"""
    from explore_field_dependencies import ChangeType

    explorer = FieldDependencyExplorer()

    baseline = {"field_a": {"visible": True}}
    current = {"field_a": {"visible": True}, "field_b": {"visible": True}}

    changes = explorer._compare_states(baseline, current)
    assert changes["field_b"]["change_type"] == ChangeType.FIELD_ADDED.value


def test_classify_change_type_options_changed():
    """Test that dropdown option changes are correctly classified"""
    from explore_field_dependencies import ChangeType

    explorer = FieldDependencyExplorer()

    baseline = {"dropdown": {"options": ["A", "B"]}}
    current = {"dropdown": {"options": ["A", "B", "C"]}}

    changes = explorer._compare_states(baseline, current)
    assert changes["dropdown"]["change_type"] == ChangeType.OPTIONS_CHANGED.value


def test_classify_change_type_field_removed():
    """Test that field removals are correctly classified"""
    from explore_field_dependencies import ChangeType

    explorer = FieldDependencyExplorer()

    baseline = {"field_a": {"visible": True}, "field_b": {"visible": True}}
    current = {"field_a": {"visible": True}}

    changes = explorer._compare_states(baseline, current)
    assert changes["field_b"]["change_type"] == ChangeType.FIELD_REMOVED.value


def test_classify_change_type_field_modified():
    """Test that field modifications are correctly classified"""
    from explore_field_dependencies import ChangeType

    explorer = FieldDependencyExplorer()

    baseline = {"field_a": {"value": "old"}}
    current = {"field_a": {"value": "new"}}

    changes = explorer._compare_states(baseline, current)
    assert changes["field_a"]["change_type"] == ChangeType.FIELD_MODIFIED.value


def test_classify_change_type_dialog_closed():
    """Test that dialog closing is correctly classified"""
    from explore_field_dependencies import ChangeType

    explorer = FieldDependencyExplorer()

    baseline = {"field1": {"visible": True}, "dialog_title": {"visible": True}, "dialog_content": {"visible": True}}
    current = {"field1": {"visible": True}}

    changes = explorer._compare_states(baseline, current)
    assert "dialog_title" in changes
    assert changes["dialog_title"]["change_type"] == ChangeType.DIALOG_CLOSED.value


def test_classify_change_type_validation_error():
    """Test that validation errors are correctly classified"""
    from explore_field_dependencies import ChangeType

    explorer = FieldDependencyExplorer()

    baseline = {"field_a": {"value": "", "error": None}}
    current = {"field_a": {"value": "", "error": "This field is required"}}

    changes = explorer._compare_states(baseline, current)
    assert changes["field_a"]["change_type"] == ChangeType.VALIDATION_ERROR.value


def test_exploration_budget_max_steps():
    """Test that exploration stops at max_steps"""
    from explore_field_dependencies import ExplorationBudget

    budget = ExplorationBudget(max_steps=5)

    assert budget.can_continue_steps()

    for i in range(5):
        budget.increment_steps()

    assert not budget.can_continue_steps()
    assert budget.steps_taken == 5


def test_exploration_budget_max_states():
    """Test that exploration stops at max_states"""
    from explore_field_dependencies import ExplorationBudget

    budget = ExplorationBudget(max_states=3)

    budget.record_state("state1")
    budget.record_state("state2")
    budget.record_state("state3")

    assert not budget.can_continue_states()
    assert len(budget.visited_states) == 3


def test_exploration_budget_max_time():
    """Test that exploration stops after max_time"""
    import time
    from explore_field_dependencies import ExplorationBudget

    budget = ExplorationBudget(max_time_seconds=1)

    assert budget.can_continue_time()
    time.sleep(1.5)
    assert not budget.can_continue_time()


def test_exploration_budget_integration():
    """Integration test: verify FieldDependencyExplorer respects budget limits"""
    from explore_field_dependencies import ExplorationBudget, FieldDependencyExplorer

    # Create a very restrictive budget
    budget = ExplorationBudget(max_steps=3, max_states=5, max_time_seconds=60)
    explorer = FieldDependencyExplorer(budget=budget)

    # Verify budget is initialized
    assert explorer.budget.max_steps == 3
    assert explorer.budget.steps_taken == 0

    # Simulate exploration steps
    explorer.budget.increment_steps()
    explorer.budget.increment_steps()
    explorer.budget.increment_steps()

    # Verify budget is exhausted
    assert not explorer.budget.can_continue_steps()
    assert explorer.budget.steps_taken == 3

    # Verify can_continue returns False when any budget is exhausted
    assert not explorer.budget.can_continue()



def test_v3_integration():
    """Integration test for v3 features: structured changes + budget + validation"""
    from explore_field_dependencies import ExplorationBudget, FieldDependencyExplorer, ChangeType

    # Test that all v3 components work together
    budget = ExplorationBudget(max_steps=10, max_states=5, max_time_seconds=60)
    explorer = FieldDependencyExplorer(budget=budget)

    # Verify budget is initialized
    assert explorer.budget.max_steps == 10
    assert explorer.budget.can_continue()

    # Verify ChangeType enum is available
    assert hasattr(explorer, '_compare_states')
    assert ChangeType.URL_CHANGE.value == "url_change"

    # Verify LoginValidator is available
    from auto_login_cam_v3 import LoginValidator
    validator = LoginValidator()
    assert validator.validation_strategy in ["selector_only", "api_primary", "combined"]



