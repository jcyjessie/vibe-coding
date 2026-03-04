#!/usr/bin/env python3
"""
CAM Field Dependency Explorer - V3

Systematically explores form field dependencies by:
1. Opening the New Routine Report form
2. Testing each dropdown option
3. Recording how other fields change
4. Capturing screenshots of each state

Usage:
    python explore_field_dependencies.py --url <cam-url> --feature-name <name>
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Error: Playwright is not installed.")
    print("Install it with: pip install playwright && playwright install chromium")
    sys.exit(1)

from enum import Enum
from dataclasses import dataclass, field
from time import time
from core.browser_factory import create_page
from core.artifacts import StepRecorder


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


class FieldDependencyExplorer:
    # Minimum number of dialog-related fields required to classify as dialog opened/closed
    MIN_DIALOG_FIELDS_THRESHOLD = 2

    def __init__(self, auth_file=".auth/state.json", output_dir="captured_data",
                 budget: ExplorationBudget = None):
        self.auth_file = Path(auth_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.page = None
        self.cleanup = None
        self.field_dependencies = {}

        # Budget control
        self.budget = budget or ExplorationBudget()

        # Note: StepRecorder will be initialized in explore_dependencies() with feature_name
        self.recorder = None

    def launch_browser(self):
        """Launch Chrome with storageState"""
        try:
            # Use BrowserFactory to create page
            self.page, self.cleanup = create_page(
                auth_file=str(self.auth_file),
                headless=False
            )

            print(f"✓ Browser launched with auth state: {self.auth_file}")
            return True

        except Exception as e:
            print(f"Error launching browser: {e}")
            return False

    def capture_screenshot(self, step_name: str, description: str, extra_data: Dict = None) -> Dict[str, Any]:
        """Capture screenshot and page info"""
        # Extract form state
        form_state = self.extract_form_state()

        # Combine form_state with extra_data
        combined_data = {"form_state": form_state}
        if extra_data:
            combined_data.update(extra_data)

        # Use StepRecorder to capture
        step_data = self.recorder.capture_step(
            page=self.page,
            step_name=step_name,
            description=description,
            extra_data=combined_data
        )

        print(f"  ✓ Step {step_data['step_number']}: {description}")
        print(f"    - Screenshot: {step_data['screenshot']}")

        return step_data

    def extract_form_state(self) -> Dict[str, Any]:
        """Extract current state of all form fields"""
        form_state = {
            "visible_fields": [],
            "field_values": {},
            "dropdown_options": {}
        }

        try:
            # Find the dialog
            dialog = self.page.locator("[role='dialog']:visible").first
            if not dialog.is_visible():
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
                        form_state["dropdown_options"][aria_label] = self._extract_dropdown_options(sel)
                except Exception:
                    continue

        except Exception as e:
            print(f"    Warning: Could not extract form state: {e}")

        return form_state

    def _extract_dropdown_options(self, element) -> list:
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
            print(f"    Warning: Could not extract dropdown options: {e}")

        return options

    def _wait_for_stability(self, page, timeout: int = 5000):
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

    def _stratified_sample(self, items: list, sample_size: int) -> list:
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

    def explore_dependencies(self, target_url: str, feature_name: str = "feature"):
        """Systematically explore field dependencies"""
        print("\n" + "="*60)
        print("FIELD DEPENDENCY EXPLORATION MODE")
        print("="*60)

        # Initialize StepRecorder with feature name
        self.recorder = StepRecorder(output_dir=str(self.output_dir), feature_name=feature_name)

        # Navigate to URL
        print(f"\nNavigating to: {target_url}")
        self.page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        self._wait_for_stability(self.page, timeout=5000)

        print(f"Current page: {self.page.url}")
        print(f"Page title: {self.page.title()}\n")

        # Step 1: Capture initial state
        self.capture_screenshot("01-initial-page", "Initial page load")

        # Step 2: Click New button
        print("\n[Step 2] Clicking 'New' button...")
        try:
            new_button = self.page.locator("button:has-text('New'):visible").first
            if new_button.is_visible():
                new_button.click(timeout=3000)
                self._wait_for_stability(self.page, timeout=3000)

                self.capture_screenshot("02-form-opened", "New routine report form opened")

                # Step 3: Explore field dependencies
                self._explore_form_fields()
            else:
                print("  ❌ 'New' button not found")
        except Exception as e:
            print(f"  ❌ Error clicking 'New' button: {e}")

        print("\n" + "="*60)
        print(f"EXPLORATION COMPLETE - {self.recorder.get_step_count()} steps captured")
        print("="*60 + "\n")

        return self.recorder.captured_steps

    def _explore_form_fields(self):
        """Systematically explore each form field and its dependencies with budget control"""
        print("\n[Step 3] Exploring form field dependencies...")

        try:
            dialog = self.page.locator("[role='dialog']:visible").first
            if not dialog.is_visible():
                print("  ❌ Dialog not visible")
                return

            # Capture baseline state before any interactions
            baseline_state = self.extract_form_state()
            state_fingerprint = json.dumps(baseline_state, sort_keys=True)
            self.budget.record_state(state_fingerprint)

            # Find all dropdowns/selects in the dialog
            dropdowns = dialog.locator("select:visible, [role='combobox']:visible, .v-select:visible").all()

            print(f"  Found {len(dropdowns)} dropdown field(s)")

            for dropdown_idx, dropdown in enumerate(dropdowns):
                # Check budget before exploring each field
                if not self.budget.can_continue():
                    print(f"\n⚠️  Budget exhausted: {self.budget.get_status()}")
                    break

                try:
                    if not dropdown.is_visible():
                        continue

                    # Get field label/identifier
                    field_label = self._get_field_label(dropdown, dropdown_idx)
                    print(f"\n  [Field {dropdown_idx + 1}] Exploring: {field_label}")
                    print(f"  Budget status: {self.budget.get_status()}")

                    # Click to open dropdown
                    dropdown.click(timeout=2000)
                    self._wait_for_stability(self.page, timeout=3000)

                    # Capture dropdown opened state
                    step_name = f"03-field-{dropdown_idx+1}-opened"
                    description = f"Opened dropdown: {field_label}"
                    self.capture_screenshot(step_name, description, {
                        "field_index": dropdown_idx,
                        "field_label": field_label
                    })

                    # Try to find and click each option
                    options = self._get_dropdown_options()
                    print(f"    Found {len(options)} option(s)")

                    # Use stratified sampling to cover beginning, middle, end
                    options_to_try = self._stratified_sample(options, sample_size=5)

                    for option_idx, option in enumerate(options_to_try):
                        # Check budget before testing each option
                        if not self.budget.can_continue():
                            print(f"\n⚠️  Budget exhausted: {self.budget.get_status()}")
                            break

                        try:
                            option_text = option.text_content().strip()
                            if not option_text or option_text in ["", "​"]:
                                continue

                            # Increment step counter for each option tested
                            self.budget.increment_steps()

                            print(f"    Testing option: {option_text} (Step {self.budget.steps_taken})")

                            # Click the option
                            option.click(timeout=2000)
                            self._wait_for_stability(self.page, timeout=3000)

                            # Capture state after selection
                            after_state = self.extract_form_state()

                            # Record state after interaction
                            state_fingerprint = json.dumps(after_state, sort_keys=True)
                            self.budget.record_state(state_fingerprint)

                            # Compare with baseline state (not chain)
                            changes = self._compare_states(baseline_state, after_state)

                            step_name = f"04-field-{dropdown_idx+1}-option-{option_idx+1}"
                            description = f"Selected '{option_text}' in {field_label}"
                            self.capture_screenshot(step_name, description, {
                                "field_index": dropdown_idx,
                                "field_label": field_label,
                                "selected_option": option_text,
                                "detected_changes": changes
                            })

                            # Record dependency
                            if changes:
                                if field_label not in self.field_dependencies:
                                    self.field_dependencies[field_label] = {}
                                self.field_dependencies[field_label][option_text] = changes

                            # If this was the last option, break
                            # Otherwise, reopen the dropdown for next option
                            if option_idx < len(options) - 1:
                                try:
                                    dropdown = dialog.locator("select:visible, [role='combobox']:visible, .v-select:visible").nth(dropdown_idx)
                                    if dropdown.is_visible():
                                        dropdown.click(timeout=2000)
                                        self._wait_for_stability(self.page, timeout=3000)
                                except Exception as e:
                                    # Can't reopen dropdown, stop testing this field
                                    break

                        except Exception as e:
                            print(f"      Warning: Could not test option {option_idx + 1}: {e}")
                            continue

                    # Close dropdown by pressing Escape
                    try:
                        self.page.keyboard.press("Escape")
                        self._wait_for_stability(self.page, timeout=3000)
                    except Exception as e:
                        # Escape key didn't work, dropdown may already be closed
                        pass

                except Exception as e:
                    print(f"    Warning: Could not explore dropdown {dropdown_idx + 1}: {e}")
                    continue

        except Exception as e:
            print(f"  Error exploring form fields: {e}")

    def _get_field_label(self, element, index: int) -> str:
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

    def _get_dropdown_options(self) -> List:
        """Get all visible dropdown options"""
        options = []

        # Try different selectors for dropdown options
        selectors = [
            "[role='option']:visible",
            "[role='menuitem']:visible",
            ".v-list-item:visible",
            "li:visible",
            "option:visible"
        ]

        for selector in selectors:
            try:
                found_options = self.page.locator(selector).all()
                if found_options and len(found_options) > 0:
                    options = found_options
                    break
            except Exception as e:
                # Selector didn't match, try next one
                continue

        return options

    def _compare_form_states(self, before: Dict, after: Dict) -> Dict[str, Any]:
        """Compare two form states and return detected changes"""
        changes = {
            "new_fields": [],
            "hidden_fields": [],
            "value_changes": {},
            "new_options": {}
        }

        # Check for new/hidden fields
        before_fields = set(before.get("visible_fields", []))
        after_fields = set(after.get("visible_fields", []))

        changes["new_fields"] = list(after_fields - before_fields)
        changes["hidden_fields"] = list(before_fields - after_fields)

        # Check for value changes
        before_values = before.get("field_values", {})
        after_values = after.get("field_values", {})

        for field_key in after_values:
            if field_key in before_values:
                if before_values[field_key] != after_values[field_key]:
                    changes["value_changes"][field_key] = {
                        "before": before_values[field_key],
                        "after": after_values[field_key]
                    }
            else:
                changes["value_changes"][field_key] = {
                    "before": None,
                    "after": after_values[field_key]
                }

        # Remove empty change categories
        changes = {k: v for k, v in changes.items() if v}

        return changes

    def _compare_states(self, baseline_state: dict, current_state: dict) -> dict:
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
                if self._is_dialog_field(field_id, current_state):
                    change_type = ChangeType.DIALOG_OPENED.value
                else:
                    change_type = ChangeType.FIELD_ADDED.value

                changes[field_id] = {
                    "change_type": change_type,
                    "current": current_props
                }
            elif baseline_state[field_id] != current_props:
                # Determine if it's options change, validation error, or field modification
                # Note: DIALOG_OPENED/CLOSED only applies to new/removed fields, not modified ones
                if self._is_options_change(baseline_state[field_id], current_props):
                    change_type = ChangeType.OPTIONS_CHANGED.value
                elif self._is_validation_error(current_props):
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
                if self._is_dialog_field(field_id, baseline_state):
                    change_type = ChangeType.DIALOG_CLOSED.value
                else:
                    change_type = ChangeType.FIELD_REMOVED.value

                changes[field_id] = {
                    "change_type": change_type,
                    "baseline": baseline_state[field_id]
                }

        return changes

    def _is_dialog_field(self, field_id: str, state: dict) -> bool:
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
            return len(dialog_items) >= self.MIN_DIALOG_FIELDS_THRESHOLD

        return False

    def _is_options_change(self, baseline_props: dict, current_props: dict) -> bool:
        """Check if change is specifically about dropdown options"""
        return ("options" in baseline_props and "options" in current_props and
                baseline_props.get("options") != current_props.get("options"))

    def _is_validation_error(self, props: dict) -> bool:
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

    def save_results(self):
        """Save captured data and dependencies to JSON files"""
        # Save captured steps using StepRecorder
        output_file = self.recorder.save_results(capture_mode="field_dependency_exploration")

        # Update the JSON to include field_dependencies
        with open(output_file, 'r', encoding='utf-8') as f:
            result = json.load(f)

        result["field_dependencies"] = self.field_dependencies

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"✓ Results saved to: {output_file}")
        print(f"✓ Screenshots saved to: {self.recorder.screenshots_dir}")

        # Print dependency summary
        if self.field_dependencies:
            print("\n" + "="*60)
            print("DETECTED FIELD DEPENDENCIES")
            print("="*60)
            for field, dependencies in self.field_dependencies.items():
                print(f"\n{field}:")
                for option, changes in dependencies.items():
                    print(f"  When '{option}' is selected:")
                    if changes.get("new_fields"):
                        print(f"    - New fields appear: {', '.join(changes['new_fields'])}")
                    if changes.get("hidden_fields"):
                        print(f"    - Fields hidden: {', '.join(changes['hidden_fields'])}")
                    if changes.get("value_changes"):
                        print(f"    - {len(changes['value_changes'])} field value(s) changed")
            print("="*60)

        return output_file

    def close(self):
        """Clean up resources"""
        if self.cleanup:
            self.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description="Explore field dependencies in CAM forms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python explore_field_dependencies.py \\
    --url https://fresh2.cammaster.org/v3/analysis/reporting/routine \\
    --feature-name routine-report
        """
    )

    parser.add_argument(
        '--url',
        required=True,
        help='CAM feature URL to explore'
    )

    parser.add_argument(
        '--feature-name',
        required=True,
        help='Feature name for output files'
    )

    parser.add_argument(
        '--auth-file',
        default='.auth/state.json',
        help='Path to authentication state file (default: .auth/state.json)'
    )

    parser.add_argument(
        '--output',
        default='captured_data',
        help='Output directory for captured data (default: captured_data)'
    )

    args = parser.parse_args()

    # Create explorer instance
    explorer = FieldDependencyExplorer(
        auth_file=args.auth_file,
        output_dir=args.output
    )

    # Launch browser
    if not explorer.launch_browser():
        sys.exit(1)

    try:
        # Run exploration
        captured_steps = explorer.explore_dependencies(target_url=args.url, feature_name=args.feature_name)

        if captured_steps:
            # Save results
            output_file = explorer.save_results()

            print("\n" + "="*60)
            print("NEXT STEPS")
            print("="*60)
            print(f"\n1. Review dependencies: {output_file}")
            print(f"2. Review screenshots: {explorer.recorder.screenshots_dir}")
            print(f"3. Use this data to document field interactions")
            print("="*60 + "\n")
        else:
            print("\nNo steps captured.")

    except KeyboardInterrupt:
        print("\n\nExploration interrupted by user.")

    except Exception as e:
        print(f"\nError during exploration: {e}")
        import traceback
        traceback.print_exc()

    finally:
        explorer.close()


if __name__ == "__main__":
    main()
