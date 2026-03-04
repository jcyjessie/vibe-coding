#!/usr/bin/env python3
"""
Field Dependencies Flow - Extracted from explore_field_dependencies.py

Provides reusable field dependency exploration functionality.
Enhanced with SelectorEngine and RetryHandler for robustness.
"""

import json
import logging
from enum import Enum
from dataclasses import dataclass, field
from time import time
from typing import List, Dict, Any

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeout
except ImportError:
    PlaywrightTimeout = TimeoutError

from selector_engine import SelectorEngine
from retry_handler import RetryHandler, RetryableError

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Semantic types of state changes for better interpretability"""
    URL_CHANGE = "url_change"
    DIALOG_OPENED = "dialog_opened"
    DIALOG_CLOSED = "dialog_closed"
    FIELD_ADDED = "field_added"
    FIELD_REMOVED = "field_removed"
    FIELD_MODIFIED = "field_modified"
    OPTIONS_CHANGED = "options_changed"
    VALIDATION_ERROR = "validation_error"


@dataclass
class ExplorationBudget:
    """
    Global budget control to prevent exploration time explosion.

    Provides hard limits on:
    - Total steps taken
    - Unique states visited
    - Total execution time
    """
    max_steps: int = 100
    max_states: int = 50
    max_time_seconds: int = 300  # 5 minutes

    # Internal tracking
    steps_taken: int = field(default=0, init=False)
    visited_states: set = field(default_factory=set, init=False)
    start_time: float = field(default_factory=time, init=False)

    def can_continue_steps(self) -> bool:
        """Check if we can take more steps"""
        return self.steps_taken < self.max_steps

    def can_continue_states(self) -> bool:
        """Check if we can visit more states"""
        return len(self.visited_states) < self.max_states

    def can_continue_time(self) -> bool:
        """Check if we have time remaining"""
        elapsed = time() - self.start_time
        return elapsed < self.max_time_seconds

    def can_continue(self) -> bool:
        """Check if exploration can continue (all budgets)"""
        return (self.can_continue_steps() and
                self.can_continue_states() and
                self.can_continue_time())

    def increment_steps(self):
        """Increment step counter"""
        self.steps_taken += 1

    def record_state(self, state_fingerprint: str):
        """Record a visited state"""
        self.visited_states.add(state_fingerprint)

    def get_status(self) -> dict:
        """Get current budget status"""
        elapsed = time() - self.start_time
        return {
            "steps": f"{self.steps_taken}/{self.max_steps}",
            "states": f"{len(self.visited_states)}/{self.max_states}",
            "time": f"{elapsed:.1f}s/{self.max_time_seconds}s",
            "can_continue": self.can_continue()
        }


# Minimum number of dialog-related fields required to classify as dialog opened/closed
MIN_DIALOG_FIELDS_THRESHOLD = 2


def extract_form_state(page, selector_engine: SelectorEngine = None) -> Dict[str, Any]:
    """Extract current state of all form fields"""
    if selector_engine is None:
        selector_engine = SelectorEngine()

    form_state = {
        "visible_fields": [],
        "field_values": {},
        "dropdown_options": {}
    }

    try:
        # Find the dialog using SelectorEngine
        dialog_selectors = selector_engine.get_fallback_selectors(
            element_type="dialog",
            role="dialog"
        )

        dialog = None
        for selector in dialog_selectors:
            try:
                dialog = page.locator(f"{selector}:visible").first
                if dialog.is_visible():
                    break
            except Exception:
                continue

        if not dialog or not dialog.is_visible():
            return form_state

        # Extract all visible labels and their associated fields
        labels = dialog.locator("label:visible").all()
        for label in labels:
            try:
                label_text = label.text_content().strip()
                if label_text:
                    form_state["visible_fields"].append(label_text)
            except Exception as e:
                # Skip labels that can't be read (stale elements, etc.)
                continue

        # Extract input field values
        inputs = dialog.locator("input:visible, textarea:visible").all()
        for idx, inp in enumerate(inputs):
            try:
                field_type = inp.get_attribute("type") or "text"
                placeholder = inp.get_attribute("placeholder") or ""
                value = inp.input_value() if field_type != "checkbox" else inp.is_checked()

                field_key = placeholder if placeholder else f"input_{idx}"
                form_state["field_values"][field_key] = {
                    "type": field_type,
                    "value": value
                }
            except Exception as e:
                # Skip inputs that can't be read (stale elements, etc.)
                continue

        # Extract select/dropdown current values
        selects = dialog.locator("select:visible, [role='combobox']:visible").all()
        for idx, sel in enumerate(selects):
            try:
                text = sel.text_content().strip() if sel.text_content() else ""
                aria_label = sel.get_attribute("aria-label") or f"dropdown_{idx}"

                form_state["field_values"][aria_label] = {
                    "type": "select",
                    "value": text
                }

                # Collect all dropdown options for <select> elements
                tag_name = sel.evaluate("el => el.tagName.toLowerCase()")
                if tag_name == "select":
                    form_state["dropdown_options"][aria_label] = extract_dropdown_options(sel)
            except Exception:
                continue

    except Exception as e:
        logger.warning(f"Could not extract form state: {e}")

    return form_state


def extract_dropdown_options(element) -> list:
    """
    Extract all options from a dropdown element.

    Args:
        element: Playwright Locator for select/dropdown

    Returns:
        List of dicts with 'value' (can be None) and 'text' keys.
        Empty options (whitespace-only text) are skipped.
    """
    options = []

    try:
        option_elements = element.locator("option").all()

        for option in option_elements:
            value = option.get_attribute("value")
            text = option.inner_text()
            text_stripped = text.strip()

            # Skip empty options
            if not text_stripped:
                continue

            options.append({"value": value, "text": text_stripped})
    except Exception as e:
        logger.warning(f"Could not extract dropdown options: {e}")

    return options


def wait_for_stability(page, timeout: int = 5000):
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
        page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception:
        # If networkidle times out, fall back to domcontentloaded
        page.wait_for_load_state("domcontentloaded", timeout=timeout)


def stratified_sample(items: list, sample_size: int) -> list:
    """
    Sample items using stratified approach to cover beginning, middle, end.

    Args:
        items: List of items to sample from
        sample_size: Number of items to sample (must be >= 0)

    Returns:
        List of sampled items (exactly sample_size items, or all items if fewer available)

    Raises:
        ValueError: If sample_size is negative

    Edge cases:
        - sample_size=0: returns empty list
        - sample_size=1: returns first item only
        - empty list: returns empty list
        - sample_size >= len(items): returns all items
    """
    # 输入验证
    if sample_size < 0:
        raise ValueError(f"sample_size must be non-negative, got {sample_size}")

    # 边界情况处理
    if sample_size == 0 or len(items) == 0:
        return []

    if sample_size == 1:
        return [items[0]]

    if len(items) <= sample_size:
        return items

    # 使用集合跟踪索引以避免重复
    indices = set()

    # 总是包含第一个和最后一个
    indices.add(0)
    indices.add(len(items) - 1)

    # 从中间均匀采样
    remaining_slots = sample_size - 2
    if remaining_slots > 0:
        # 计算步长以均匀分布
        step = (len(items) - 1) / (remaining_slots + 1)
        for i in range(1, remaining_slots + 1):
            idx = int(i * step)
            indices.add(idx)

    # 如果由于重复导致索引不足，从剩余位置补充
    if len(indices) < sample_size:
        available = set(range(len(items))) - indices
        needed = sample_size - len(indices)
        # 均匀选择剩余位置
        available_list = sorted(available)
        step = len(available_list) / needed if needed > 0 else 0
        for i in range(needed):
            idx = int(i * step)
            if idx < len(available_list):
                indices.add(available_list[idx])

    # 按原始顺序返回采样项
    return [items[i] for i in sorted(indices)]


def get_field_label(element, index: int) -> str:
    """Try to get the label for a form field"""
    try:
        # Try to find associated label
        aria_label = element.get_attribute("aria-label")
        if aria_label:
            return aria_label

        # Try to find nearby label element
        parent = element.locator("xpath=ancestor::div[contains(@class, 'form') or contains(@class, 'field')][1]").first
        if parent.is_visible():
            label = parent.locator("label").first
            if label.is_visible():
                return label.text_content().strip()

        # Try to get text content
        text = element.text_content().strip()
        if text and text != "​":
            return text

    except Exception as e:
        # Can't determine label, use fallback
        pass

    return f"Field_{index + 1}"


def get_dropdown_options(page, selector_engine: SelectorEngine = None) -> List:
    """Get all visible dropdown options"""
    if selector_engine is None:
        selector_engine = SelectorEngine()

    options = []

    # Use SelectorEngine for robust option selection
    option_selectors = [
        "[role='option']:visible",
        "[role='menuitem']:visible",
        ".v-list-item:visible",
        "li:visible",
        "option:visible"
    ]

    for selector in option_selectors:
        try:
            found_options = page.locator(selector).all()
            if found_options and len(found_options) > 0:
                options = found_options
                break
        except Exception as e:
            # Selector didn't match, try next one
            continue

    return options


def is_dialog_field(field_id: str, state: dict) -> bool:
    """
    Check if field is part of a dialog based on naming patterns.

    For individual fields: Returns True if field_id contains dialog keywords
    For visible_fields list: Returns True if list contains >= MIN_DIALOG_FIELDS_THRESHOLD dialog items

    This ensures consistent threshold-based detection across both scenarios.
    """
    dialog_keywords = ["dialog", "modal", "popup", "overlay"]

    # Check if field_id itself contains dialog keywords
    if any(keyword in field_id.lower() for keyword in dialog_keywords):
        return True

    # Special case: check if visible_fields list contains dialog-related items
    if field_id == "visible_fields" and isinstance(state.get(field_id), list):
        visible_items = state.get(field_id, [])
        dialog_items = [item for item in visible_items
                      if any(keyword in str(item).lower() for keyword in dialog_keywords)]
        # Consider it a dialog if threshold number of dialog-related items are present
        return len(dialog_items) >= MIN_DIALOG_FIELDS_THRESHOLD

    return False


def is_options_change(baseline_props: dict, current_props: dict) -> bool:
    """Check if change is specifically about dropdown options"""
    return ("options" in baseline_props and "options" in current_props and
            baseline_props.get("options") != current_props.get("options"))


def is_validation_error(props: dict) -> bool:
    """
    Check if field shows validation error by examining specific keys.

    Checks for error indicators in common validation-related keys:
    - 'error': Error message field
    - 'validation': Validation state field
    - 'invalid': Invalid flag field
    - 'required': Required field violation

    Returns True if any of these keys exist and have truthy values.
    """
    if not isinstance(props, dict):
        return False

    # Check specific validation-related keys
    validation_keys = ['error', 'validation', 'invalid', 'required']
    for key in validation_keys:
        if key in props and props[key]:
            return True

    return False


def compare_states(baseline_state: dict, current_state: dict) -> dict:
    """
    Compare current state against baseline to detect changes with semantic types.

    Classification priority for field modifications (checked in order):
    1. DIALOG_OPENED/CLOSED - Field contains dialog-related keywords
    2. OPTIONS_CHANGED - Dropdown options list changed
    3. VALIDATION_ERROR - Field has error/validation indicators
    4. FIELD_MODIFIED - Generic field value change (fallback)

    For new fields:
    - DIALOG_OPENED if field matches dialog patterns
    - FIELD_ADDED otherwise

    For removed fields:
    - DIALOG_CLOSED if field matches dialog patterns
    - FIELD_REMOVED otherwise

    Args:
        baseline_state: The initial state before any actions
        current_state: The state after an action

    Returns:
        Dictionary of fields that changed from baseline with semantic change_type
    """
    changes = {}

    # Check for URL change
    if baseline_state.get("url") != current_state.get("url"):
        changes["url"] = {
            "change_type": ChangeType.URL_CHANGE.value,
            "baseline": baseline_state.get("url"),
            "current": current_state.get("url")
        }

    # Check for new or changed fields
    for field_id, current_props in current_state.items():
        if field_id == "url":
            continue  # Already handled

        if field_id not in baseline_state:
            # Classify as dialog opened if multiple fields with "dialog" appear
            if is_dialog_field(field_id, current_state):
                change_type = ChangeType.DIALOG_OPENED.value
            else:
                change_type = ChangeType.FIELD_ADDED.value

            changes[field_id] = {
                "change_type": change_type,
                "current": current_props
            }
        elif baseline_state[field_id] != current_props:
            # Note: DIALOG_OPENED/CLOSED only applies to new/removed fields, not modified ones
            if is_options_change(baseline_state[field_id], current_props):
                change_type = ChangeType.OPTIONS_CHANGED.value
            elif is_validation_error(current_props):
                change_type = ChangeType.VALIDATION_ERROR.value
            else:
                change_type = ChangeType.FIELD_MODIFIED.value

            changes[field_id] = {
                "change_type": change_type,
                "baseline": baseline_state[field_id],
                "current": current_props
            }

    # Check for removed fields
    for field_id in baseline_state:
        if field_id == "url":
            continue

        if field_id not in current_state:
            # Classify as dialog closed if multiple fields with "dialog" disappear
            if is_dialog_field(field_id, baseline_state):
                change_type = ChangeType.DIALOG_CLOSED.value
            else:
                change_type = ChangeType.FIELD_REMOVED.value

            changes[field_id] = {
                "change_type": change_type,
                "baseline": baseline_state[field_id]
            }

    return changes


def explore_form_fields(page, recorder, budget: ExplorationBudget, field_dependencies: dict,
                        selector_engine: SelectorEngine = None, retry_handler: RetryHandler = None):
    """Systematically explore each form field and its dependencies with budget control"""
    logger.info("\n[Step 3] Exploring form field dependencies...")

    if selector_engine is None:
        selector_engine = SelectorEngine()
    if retry_handler is None:
        retry_handler = RetryHandler(max_retries=3, base_delay=1.0)

    try:
        # Find dialog using SelectorEngine
        dialog_selectors = selector_engine.get_fallback_selectors(
            element_type="dialog",
            role="dialog"
        )

        dialog = None
        for selector in dialog_selectors:
            try:
                dialog = page.locator(f"{selector}:visible").first
                if dialog.is_visible():
                    break
            except Exception:
                continue

        if not dialog or not dialog.is_visible():
            logger.error("Dialog not visible")
            return

        # Capture baseline state before any interactions
        baseline_state = extract_form_state(page, selector_engine)
        state_fingerprint = json.dumps(baseline_state, sort_keys=True)
        budget.record_state(state_fingerprint)

        # Find all dropdowns/selects in the dialog
        dropdowns = dialog.locator("select:visible, [role='combobox']:visible, .v-select:visible").all()

        logger.info(f"  Found {len(dropdowns)} dropdown field(s)")

        for dropdown_idx, dropdown in enumerate(dropdowns):
            # Check budget before exploring each field
            if not budget.can_continue():
                logger.warning(f"\n⚠️  Budget exhausted: {budget.get_status()}")
                break

            try:
                if not dropdown.is_visible():
                    continue

                # Get field label/identifier
                field_label = get_field_label(dropdown, dropdown_idx)
                logger.info(f"\n  [Field {dropdown_idx + 1}] Exploring: {field_label}")
                logger.info(f"  Budget status: {budget.get_status()}")

                # Click to open dropdown with retry
                def click_dropdown():
                    if not dropdown.is_visible():
                        raise RetryableError("Dropdown not visible")
                    dropdown.click(timeout=2000)
                    wait_for_stability(page, timeout=3000)

                try:
                    retry_handler.execute(click_dropdown)
                except RetryableError as e:
                    logger.warning(f"Failed to open dropdown after retries: {e}")
                    continue

                # Capture dropdown opened state
                step_name = f"03-field-{dropdown_idx+1}-opened"
                description = f"Opened dropdown: {field_label}"

                # Extract form state
                form_state = extract_form_state(page, selector_engine)
                combined_data = {
                    "form_state": form_state,
                    "field_index": dropdown_idx,
                    "field_label": field_label
                }

                recorder.capture_step(
                    page=page,
                    step_name=step_name,
                    description=description,
                    extra_data=combined_data
                )

                # Try to find and click each option
                options = get_dropdown_options(page, selector_engine)
                logger.info(f"    Found {len(options)} option(s)")

                # Use stratified sampling to cover beginning, middle, end
                options_to_try = stratified_sample(options, sample_size=5)

                for option_idx, option in enumerate(options_to_try):
                    # Check budget before testing each option
                    if not budget.can_continue():
                        logger.warning(f"\n⚠️  Budget exhausted: {budget.get_status()}")
                        break

                    try:
                        option_text = option.text_content().strip()
                        if not option_text or option_text in ["", "​"]:
                            continue

                        # Increment step counter for each option tested
                        budget.increment_steps()

                        logger.info(f"    Testing option: {option_text} (Step {budget.steps_taken})")

                        # Click the option with retry
                        def click_option():
                            if not option.is_visible():
                                raise RetryableError("Option not visible")
                            option.click(timeout=2000)
                            wait_for_stability(page, timeout=3000)

                        try:
                            retry_handler.execute(click_option)
                        except RetryableError as e:
                            logger.warning(f"Failed to click option after retries: {e}")
                            continue

                        # Capture state after selection
                        after_state = extract_form_state(page, selector_engine)

                        # Record state after interaction
                        state_fingerprint = json.dumps(after_state, sort_keys=True)
                        budget.record_state(state_fingerprint)

                        # Compare with baseline state (not chain)
                        changes = compare_states(baseline_state, after_state)

                        step_name = f"04-field-{dropdown_idx+1}-option-{option_idx+1}"
                        description = f"Selected '{option_text}' in {field_label}"

                        combined_data = {
                            "form_state": after_state,
                            "field_index": dropdown_idx,
                            "field_label": field_label,
                            "selected_option": option_text,
                            "detected_changes": changes
                        }

                        recorder.capture_step(
                            page=page,
                            step_name=step_name,
                            description=description,
                            extra_data=combined_data
                        )

                        # Record dependency
                        if changes:
                            if field_label not in field_dependencies:
                                field_dependencies[field_label] = {}
                            field_dependencies[field_label][option_text] = changes

                        # If this was the last option, break
                        # Otherwise, reopen the dropdown for next option
                        if option_idx < len(options) - 1:
                            def reopen_dropdown():
                                dropdown_elem = dialog.locator("select:visible, [role='combobox']:visible, .v-select:visible").nth(dropdown_idx)
                                if not dropdown_elem.is_visible():
                                    raise RetryableError("Dropdown not visible for reopening")
                                dropdown_elem.click(timeout=2000)
                                wait_for_stability(page, timeout=3000)

                            try:
                                retry_handler.execute(reopen_dropdown)
                            except RetryableError as e:
                                logger.warning(f"Failed to reopen dropdown: {e}")
                                break

                    except Exception as e:
                        logger.warning(f"      Could not test option {option_idx + 1}: {e}")
                        continue

                # Close dropdown by pressing Escape
                try:
                    page.keyboard.press("Escape")
                    wait_for_stability(page, timeout=3000)
                except Exception as e:
                    # Escape key didn't work, dropdown may already be closed
                    pass

            except Exception as e:
                logger.warning(f"    Could not explore dropdown {dropdown_idx + 1}: {e}")
                continue

    except Exception as e:
        logger.error(f"  Error exploring form fields: {e}")


def explore_dependencies_flow(page, recorder, target_url: str, budget: ExplorationBudget = None,
                             selector_engine: SelectorEngine = None, retry_handler: RetryHandler = None):
    """Systematically explore field dependencies"""
    logger.info("\n" + "="*60)
    logger.info("FIELD DEPENDENCY EXPLORATION MODE")
    logger.info("="*60)

    # Initialize dependencies if not provided
    if budget is None:
        budget = ExplorationBudget()
    if selector_engine is None:
        selector_engine = SelectorEngine()
    if retry_handler is None:
        retry_handler = RetryHandler(max_retries=3, base_delay=1.0)

    field_dependencies = {}

    # Navigate to URL
    logger.info(f"\nNavigating to: {target_url}")
    page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
    wait_for_stability(page, timeout=5000)

    logger.info(f"Current page: {page.url}")
    logger.info(f"Page title: {page.title()}\n")

    # Step 1: Capture initial state
    recorder.capture_step(page, "01-initial-page", "Initial page load")

    # Step 2: Click New button with retry
    logger.info("\n[Step 2] Clicking 'New' button...")
    try:
        # Use SelectorEngine for robust button selection
        new_button_selectors = selector_engine.get_fallback_selectors(
            element_type="button",
            text="New",
            aria_label="New"
        )

        new_button = None
        for selector in new_button_selectors:
            try:
                buttons = page.locator(f"{selector}:visible").all()
                if buttons:
                    new_button = buttons[0]
                    break
            except Exception:
                continue

        if new_button and new_button.is_visible():
            # Click with retry
            def click_new_button():
                if not new_button.is_visible():
                    raise RetryableError("New button not visible")
                new_button.click(timeout=3000)
                wait_for_stability(page, timeout=3000)

            try:
                retry_handler.execute(click_new_button)
                recorder.capture_step(page, "02-form-opened", "New routine report form opened")

                # Step 3: Explore field dependencies
                explore_form_fields(page, recorder, budget, field_dependencies, selector_engine, retry_handler)
            except RetryableError as e:
                logger.error(f"Failed to click 'New' button after retries: {e}")
        else:
            logger.error("'New' button not found")
    except Exception as e:
        logger.error(f"Error clicking 'New' button: {e}")

    logger.info("\n" + "="*60)
    logger.info(f"EXPLORATION COMPLETE - {recorder.get_step_count()} steps captured")
    logger.info("="*60 + "\n")

    return field_dependencies
