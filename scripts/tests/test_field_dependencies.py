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
