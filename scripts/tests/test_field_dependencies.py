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

