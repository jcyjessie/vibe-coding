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
