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

    class MockDropdown:
        def __init__(self):
            self.options = [
                MockOption("opt1", "Option 1"),
                MockOption("opt2", "Option 2"),
                MockOption("opt3", "Option 3")
            ]

        def query_selector_all(self, selector):
            if selector == "option":
                return self.options
            return []

    mock_dropdown = MockDropdown()
    result = explorer._extract_dropdown_options(mock_dropdown)

    assert len(result) == 3
    assert result[0]["value"] == "opt1"
    assert result[0]["text"] == "Option 1"
    assert result[1]["value"] == "opt2"
    assert result[1]["text"] == "Option 2"
    assert result[2]["value"] == "opt3"
    assert result[2]["text"] == "Option 3"
