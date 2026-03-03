#!/usr/bin/env python3
"""
CAM Field Dependency Explorer - V2

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


class FieldDependencyExplorer:
    def __init__(self, auth_file=".auth/state.json", output_dir="captured_data"):
        self.auth_file = Path(auth_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.screenshots_dir = self.output_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.captured_steps = []
        self.step_counter = 1
        self.field_dependencies = {}

    def launch_browser(self):
        """Launch Chrome with storageState"""
        try:
            if not self.auth_file.exists():
                print(f"❌ Auth file not found: {self.auth_file}")
                print("Please run auto_login_cam_v2.py first to log in.")
                return False

            self.playwright = sync_playwright().start()

            # Launch browser with proxy
            self.browser = self.playwright.chromium.launch(
                headless=False,
                channel="chrome",
                proxy={"server": "http://localhost:7890"}
            )

            # Create context with saved authentication state
            self.context = self.browser.new_context(
                storage_state=str(self.auth_file),
                viewport={"width": 1920, "height": 1080}
            )

            # Create new page
            self.page = self.context.new_page()

            print(f"✓ Browser launched with auth state: {self.auth_file}")
            return True

        except Exception as e:
            print(f"Error launching browser: {e}")
            return False

    def capture_screenshot(self, step_name: str, description: str, extra_data: Dict = None) -> Dict[str, Any]:
        """Capture screenshot and page info"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_filename = f"{step_name}_{timestamp}.png"
        screenshot_path = self.screenshots_dir / screenshot_filename

        # Take screenshot
        self.page.screenshot(path=str(screenshot_path), full_page=False)

        # Extract page information
        page_info = {
            "step_number": self.step_counter,
            "step_name": step_name,
            "description": description,
            "url": self.page.url,
            "title": self.page.title(),
            "screenshot": str(screenshot_filename),
            "timestamp": timestamp
        }

        if extra_data:
            page_info.update(extra_data)

        # Extract form state
        page_info["form_state"] = self.extract_form_state()

        print(f"  ✓ Step {self.step_counter}: {description}")
        print(f"    - Screenshot: {screenshot_filename}")

        self.captured_steps.append(page_info)
        self.step_counter += 1

        return page_info

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
                except:
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
                except:
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
                except:
                    continue

        except Exception as e:
            print(f"    Warning: Could not extract form state: {e}")

        return form_state

    def explore_dependencies(self, target_url: str):
        """Systematically explore field dependencies"""
        print("\n" + "="*60)
        print("FIELD DEPENDENCY EXPLORATION MODE")
        print("="*60)

        # Navigate to URL
        print(f"\nNavigating to: {target_url}")
        self.page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        self.page.wait_for_timeout(3000)

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
                self.page.wait_for_timeout(2000)

                self.capture_screenshot("02-form-opened", "New routine report form opened")

                # Step 3: Explore field dependencies
                self._explore_form_fields()
            else:
                print("  ❌ 'New' button not found")
        except Exception as e:
            print(f"  ❌ Error clicking 'New' button: {e}")

        print("\n" + "="*60)
        print(f"EXPLORATION COMPLETE - {len(self.captured_steps)} steps captured")
        print("="*60 + "\n")

        return self.captured_steps

    def _explore_form_fields(self):
        """Systematically explore each form field and its dependencies"""
        print("\n[Step 3] Exploring form field dependencies...")

        try:
            dialog = self.page.locator("[role='dialog']:visible").first
            if not dialog.is_visible():
                print("  ❌ Dialog not visible")
                return

            # Capture baseline state before any interactions
            baseline_state = self.extract_form_state()

            # Find all dropdowns/selects in the dialog
            dropdowns = dialog.locator("select:visible, [role='combobox']:visible, .v-select:visible").all()

            print(f"  Found {len(dropdowns)} dropdown field(s)")

            for dropdown_idx, dropdown in enumerate(dropdowns):
                try:
                    if not dropdown.is_visible():
                        continue

                    # Get field label/identifier
                    field_label = self._get_field_label(dropdown, dropdown_idx)
                    print(f"\n  [Field {dropdown_idx + 1}] Exploring: {field_label}")

                    # Click to open dropdown
                    dropdown.click(timeout=2000)
                    self.page.wait_for_timeout(1000)

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

                    for option_idx, option in enumerate(options[:5]):  # Limit to first 5 options
                        try:
                            option_text = option.text_content().strip()
                            if not option_text or option_text in ["", "​"]:
                                continue

                            print(f"    Testing option: {option_text}")

                            # Click the option
                            option.click(timeout=2000)
                            self.page.wait_for_timeout(1500)

                            # Capture state after selection
                            after_state = self.extract_form_state()

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
                                        self.page.wait_for_timeout(800)
                                except:
                                    break

                        except Exception as e:
                            print(f"      Warning: Could not test option {option_idx + 1}: {e}")
                            continue

                    # Close dropdown by pressing Escape
                    try:
                        self.page.keyboard.press("Escape")
                        self.page.wait_for_timeout(500)
                    except:
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

        except:
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
            except:
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
        Compare current state against baseline to detect changes.

        Args:
            baseline_state: The initial state before any actions
            current_state: The state after an action

        Returns:
            Dictionary of fields that changed from baseline
        """
        changes = {}

        # Check for new or changed fields
        for field_id, current_props in current_state.items():
            if field_id not in baseline_state:
                changes[field_id] = {
                    "change_type": "appeared",
                    "current": current_props
                }
            elif baseline_state[field_id] != current_props:
                changes[field_id] = {
                    "change_type": "modified",
                    "baseline": baseline_state[field_id],
                    "current": current_props
                }

        # Check for removed fields
        for field_id in baseline_state:
            if field_id not in current_state:
                changes[field_id] = {
                    "change_type": "disappeared",
                    "baseline": baseline_state[field_id]
                }

        return changes

    def save_results(self, feature_name="feature"):
        """Save captured data and dependencies to JSON files"""
        # Save captured steps
        output_file = self.output_dir / f"{feature_name}_dependencies.json"

        result = {
            "feature_name": feature_name,
            "capture_date": datetime.now().isoformat(),
            "capture_mode": "field_dependency_exploration",
            "total_steps": len(self.captured_steps),
            "field_dependencies": self.field_dependencies,
            "steps": self.captured_steps
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"✓ Results saved to: {output_file}")
        print(f"✓ Screenshots saved to: {self.screenshots_dir}")

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
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


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
        captured_steps = explorer.explore_dependencies(target_url=args.url)

        if captured_steps:
            # Save results
            output_file = explorer.save_results(args.feature_name)

            print("\n" + "="*60)
            print("NEXT STEPS")
            print("="*60)
            print(f"\n1. Review dependencies: {output_file}")
            print(f"2. Review screenshots: {explorer.screenshots_dir}")
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
