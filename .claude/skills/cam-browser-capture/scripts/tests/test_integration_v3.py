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
