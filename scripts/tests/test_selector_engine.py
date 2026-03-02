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
