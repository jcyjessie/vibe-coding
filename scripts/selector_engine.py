from enum import Enum
from typing import Optional, List


class SelectorPriority(Enum):
    """Priority order for selector strategies"""
    DATA_TESTID = 1
    ARIA_LABEL = 2
    ROLE = 3
    TEXT = 4


class SelectorEngine:
    """Builds robust selectors with fallback strategies"""

    def build_selector(
        self,
        element_type: str,
        data_testid: Optional[str] = None,
        aria_label: Optional[str] = None,
        role: Optional[str] = None,
        text: Optional[str] = None
    ) -> str:
        """Build selector using highest priority available attribute"""

        if data_testid:
            return f"[data-testid='{data_testid}']"

        if aria_label:
            return f"[aria-label='{aria_label}']"

        if role:
            return f"[role='{role}']"

        if text:
            return f"{element_type}:has-text('{text}')"

        # Fallback to element type only
        return element_type

    def get_fallback_selectors(
        self,
        element_type: str,
        data_testid: Optional[str] = None,
        aria_label: Optional[str] = None,
        role: Optional[str] = None,
        text: Optional[str] = None
    ) -> List[str]:
        """Get list of selectors in priority order for fallback"""
        selectors = []

        if data_testid:
            selectors.append(f"[data-testid='{data_testid}']")

        if aria_label:
            selectors.append(f"[aria-label='{aria_label}']")

        if role:
            selectors.append(f"[role='{role}']")

        if text:
            selectors.append(f"{element_type}:has-text('{text}')")

        return selectors
