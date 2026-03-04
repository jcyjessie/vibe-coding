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
