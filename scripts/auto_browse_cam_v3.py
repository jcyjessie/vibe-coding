#!/usr/bin/env python3
"""
CAM Browser Capture - V3 (State Tracking)

Adds state tracking infrastructure to detect and skip duplicate states.
Uses StateTracker, SelectorEngine, and RetryHandler modules.

Usage:
    python auto_browse_cam_v3.py --url <cam-url> --feature-name <name> --auth-file .auth/state.json
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Error: Playwright is not installed.")
    print("Install it with: pip install playwright && playwright install chromium")
    sys.exit(1)

from state_tracker import StateTracker
from selector_engine import SelectorEngine
from retry_handler import RetryHandler, RetryableError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CAMCaptureV3:
    def __init__(self, auth_file=".auth/state.json", output_dir="captured_data", headless=False):
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
        self.headless = headless

        # 初始化状态跟踪模块
        self.state_tracker = StateTracker()
        self.selector_engine = SelectorEngine()
        self.retry_handler = RetryHandler(max_retries=3, base_delay=1.0)

    def launch_browser(self):
        """Launch Chrome with storageState (Kintsugi style)"""
        try:
            if not self.auth_file.exists():
                print(f"❌ Auth file not found: {self.auth_file}")
                print("Please run auto_login_cam_v2.py first to log in.")
                return False

            self.playwright = sync_playwright().start()

            # Launch browser with proxy
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
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

    def _detect_state_change(self) -> Dict[str, Any]:
        """检测当前页面状态（用于后续任务的状态跟踪）"""
        try:
            state = {
                "url": self.page.url,
                "title": self.page.title(),
                "visible_buttons": [],
                "visible_inputs": [],
                "visible_dropdowns": []
            }

            # 提取可见按钮
            try:
                buttons = self.page.locator("button:visible").all()
                state["visible_buttons"] = [
                    btn.text_content().strip()
                    for btn in buttons[:30]
                    if btn.text_content() and btn.text_content().strip()
                ]
            except:
                pass

            # 提取可见输入框
            try:
                inputs = self.page.locator("input:visible, textarea:visible").all()
                state["visible_inputs"] = [
                    inp.get_attribute("placeholder") or inp.get_attribute("name") or ""
                    for inp in inputs[:30]
                ]
            except:
                pass

            # 提取可见下拉框
            try:
                dropdowns = self.page.locator("select:visible, [role='combobox']:visible").all()
                state["visible_dropdowns"] = [
                    sel.get_attribute("name") or sel.get_attribute("aria-label") or ""
                    for sel in dropdowns[:20]
                ]
            except:
                pass

            return state

        except Exception as e:
            logger.error(f"Error detecting state: {e}")
            return {}

    def capture_screenshot(self, step_name: str, description: str) -> Optional[Dict[str, Any]]:
        """Capture screenshot and page info, skip if duplicate state"""
        # 检测当前状态
        current_state = self._detect_state_change()

        # 检查是否为重复状态
        if self.state_tracker.is_duplicate(current_state):
            logger.info(f"Skipping duplicate state: {step_name}")
            return None

        # 记录新状态
        self.state_tracker.add_state(current_state)

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

        # Extract visible buttons
        try:
            buttons = self.page.locator("button:visible").all()
            page_info["buttons"] = [
                btn.text_content().strip()
                for btn in buttons[:30]
                if btn.text_content() and btn.text_content().strip()
            ]
        except:
            page_info["buttons"] = []

        # Extract input fields
        try:
            inputs = self.page.locator("input:visible, textarea:visible").all()
            page_info["input_fields"] = [
                {
                    "placeholder": inp.get_attribute("placeholder") or "",
                    "name": inp.get_attribute("name") or "",
                    "type": inp.get_attribute("type") or "text"
                }
                for inp in inputs[:30]
            ]
        except:
            page_info["input_fields"] = []

        # Extract dropdowns/selects
        try:
            selects = self.page.locator("select:visible, [role='combobox']:visible").all()
            page_info["dropdowns"] = [
                {
                    "name": sel.get_attribute("name") or sel.get_attribute("aria-label") or "",
                    "text": sel.text_content().strip() if sel.text_content() else ""
                }
                for sel in selects[:20]
            ]
        except:
            page_info["dropdowns"] = []

        print(f"  ✓ Step {self.step_counter}: {description}")
        print(f"    - Screenshot: {screenshot_filename}")
        print(f"    - Buttons: {len(page_info.get('buttons', []))}, Inputs: {len(page_info.get('input_fields', []))}, Dropdowns: {len(page_info.get('dropdowns', []))}")

        self.step_counter += 1

        return page_info

    def automatic_capture(self, target_url: str):
        """Automatically explore and capture the page"""
        print("\n" + "="*60)
        print("AUTOMATIC CAPTURE MODE - V3 (STATE TRACKING)")
        print("="*60)

        # Navigate to URL
        print(f"\nNavigating to: {target_url}")
        self.page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        self.page.wait_for_timeout(3000)  # Wait for page to fully load

        print(f"Current page: {self.page.url}")
        print(f"Page title: {self.page.title()}\n")

        # Step 1: Capture initial state
        result = self.capture_screenshot("01-initial-page", "Initial page load")
        if result:
            self.captured_steps.append(result)

        # Step 2: Find and capture interactive elements
        self._capture_interactive_elements()

        # Step 3: Capture any modals or dialogs
        self._capture_modals()

        print("\n" + "="*60)
        print(f"CAPTURE COMPLETE - {len(self.captured_steps)} steps captured")
        print("="*60 + "\n")

        return self.captured_steps

    def _capture_interactive_elements(self):
        """Find and interact with dropdowns, buttons, date pickers"""
        print("\n[Phase 2] Exploring interactive elements...")

        # Priority 1: Look for "New" button first (common in CAM for creating configs)
        print("\n  [Priority] Looking for 'New' button...")
        try:
            new_buttons = self.page.locator("button:has-text('New'):visible").all()
            if new_buttons:
                print(f"  Found {len(new_buttons)} 'New' button(s)")
                for idx, btn in enumerate(new_buttons[:1]):  # Only click first one
                    try:
                        if btn.is_visible():
                            print(f"  Clicking 'New' button...")
                            btn.click(timeout=3000)
                            self.page.wait_for_timeout(2000)

                            # Capture the opened dialog/form
                            step_name = f"02-new-button-clicked"
                            description = "Clicked 'New' button - configuration form opened"
                            result = self.capture_screenshot(step_name, description)
                            if result:
                                self.captured_steps.append(result)

                            # Try to capture form fields in the dialog
                            self._capture_dialog_fields()

                            # Close dialog if there's a close button
                            try:
                                close_btns = self.page.locator("button:has-text('Cancel'):visible, button:has-text('Close'):visible").all()
                                if close_btns:
                                    close_btns[0].click(timeout=2000)
                                    self.page.wait_for_timeout(1000)
                            except:
                                pass
                    except Exception as e:
                        print(f"  Could not interact with 'New' button: {e}")
                        continue
        except Exception as e:
            print(f"  No 'New' button found or error: {e}")

        # Look for common CAM UI patterns
        selectors_to_try = [
            # Tab menu buttons (more specific selectors first)
            (".tab-item button:visible", "tab menu button"),
            (".tab-wrapper .v-menu button:visible", "tab menu button"),

            # General menu buttons
            ("button[aria-label='menu']:visible", "menu button"),
            (".v-menu button:visible", "menu button"),

            # Date/time pickers
            ("[data-testid*='date']", "date picker"),
            ("[data-testid*='time']", "time selector"),
            ("[class*='date-picker']", "date picker"),
            ("[class*='time-picker']", "time picker"),

            # Dropdowns
            ("select:visible", "dropdown"),
            ("[role='combobox']:visible", "dropdown"),
            ("[class*='select']:visible", "select dropdown"),

            # Buttons that might open dialogs
            ("button:has-text('Filter'):visible", "filter button"),
            ("button:has-text('Export'):visible", "export button"),
            ("button:has-text('Settings'):visible", "settings button"),
            ("button:has-text('Add'):visible", "add button"),
            ("button:has-text('Share'):visible", "share button"),
            ("button:has-text('Copy'):visible", "copy button"),
            ("button:has-text('Delete'):visible", "delete button"),
        ]

        for selector, element_type in selectors_to_try:
            try:
                elements = self.page.locator(selector).all()
                if elements:
                    print(f"\n  Found {len(elements)} {element_type}(s)")

                    # Try to interact with the first one
                    for idx, element in enumerate(elements[:3]):  # Limit to first 3
                        try:
                            if not element.is_visible():
                                continue

                            # Get element text for description
                            element_text = element.text_content().strip() if element.text_content() else element_type

                            # Click to open
                            element.click(timeout=2000)
                            self.page.wait_for_timeout(1000)

                            # Capture opened state
                            step_name = f"02-{element_type.replace(' ', '-')}-{idx+1}-open"
                            description = f"Opened {element_type}: {element_text}"
                            result = self.capture_screenshot(step_name, description)
                            if result:
                                self.captured_steps.append(result)

                            # If it's a menu button, try to explore menu items
                            if "menu" in element_type:
                                self._explore_menu_items(element_type, idx)

                            # Click elsewhere to close (if it's a dropdown)
                            if "dropdown" in element_type or "picker" in element_type:
                                try:
                                    self.page.keyboard.press("Escape")
                                    self.page.wait_for_timeout(500)
                                except:
                                    pass

                            break  # Only interact with first visible element of each type

                        except Exception as e:
                            # Element might not be clickable, skip it
                            continue

            except Exception as e:
                # Selector might not match anything, continue
                continue

    def _explore_menu_items(self, menu_type: str, menu_idx: int):
        """After opening a menu, try to click each menu item to capture workflows"""
        print(f"\n  [Menu] Exploring menu items...")

        try:
            # Wait for menu to fully appear
            self.page.wait_for_timeout(1000)

            # Common selectors for menu items in Vuetify/CAM
            menu_item_selectors = [
                "[role='menu'] [role='menuitem']:visible",
                ".v-menu__content [role='menuitem']:visible",
                ".v-list-item:visible",
                ".v-menu__content .v-list-item:visible",
            ]

            menu_items = []
            for selector in menu_item_selectors:
                try:
                    items = self.page.locator(selector).all()
                    if items and len(items) > 0:
                        menu_items = items
                        print(f"  Found {len(menu_items)} menu item(s) using selector: {selector}")
                        break
                except:
                    continue

            if not menu_items:
                print("  No menu items found")
                return

            # Try to click each menu item
            for item_idx, item in enumerate(menu_items[:5]):  # Limit to first 5 items
                try:
                    if not item.is_visible():
                        continue

                    # Get menu item text
                    item_text = item.text_content().strip() if item.text_content() else f"item-{item_idx+1}"
                    print(f"  Clicking menu item: {item_text}")

                    # Click the menu item
                    item.click(timeout=2000)
                    self.page.wait_for_timeout(1500)

                    # Capture the result (could be a dialog, confirmation, or action)
                    step_name = f"03-{menu_type.replace(' ', '-')}-{menu_idx+1}-{item_text.lower().replace(' ', '-')}"
                    description = f"Clicked menu item: {item_text}"
                    result = self.capture_screenshot(step_name, description)
                    if result:
                        self.captured_steps.append(result)

                    # Check if a dialog appeared and capture its fields
                    try:
                        dialog_visible = self.page.locator("[role='dialog']:visible, .v-dialog--active:visible").count() > 0
                        if dialog_visible:
                            print(f"  Dialog appeared after clicking '{item_text}'")
                            self._capture_dialog_fields()

                            # Close the dialog
                            close_buttons = self.page.locator("button:has-text('Cancel'):visible, button:has-text('Close'):visible, button:has-text('×'):visible").all()
                            if close_buttons:
                                close_buttons[0].click(timeout=2000)
                                self.page.wait_for_timeout(1000)
                                print(f"  Closed dialog")
                    except:
                        pass

                    # Re-open the menu for the next item (menu might have closed)
                    # Find the original menu button again
                    try:
                        if item_idx < len(menu_items) - 1:  # Not the last item
                            # Try to find and click the menu button again
                            menu_button_selectors = [
                                ".tab-item button:visible",
                                ".tab-wrapper .v-menu button:visible",
                                "button[aria-label='menu']:visible",
                            ]
                            for btn_selector in menu_button_selectors:
                                try:
                                    btns = self.page.locator(btn_selector).all()
                                    if btns and len(btns) > menu_idx:
                                        if btns[menu_idx].is_visible():
                                            btns[menu_idx].click(timeout=2000)
                                            self.page.wait_for_timeout(1000)
                                            print(f"  Re-opened menu for next item")
                                            break
                                except:
                                    continue
                    except:
                        pass

                except Exception as e:
                    print(f"  Could not interact with menu item: {e}")
                    continue

        except Exception as e:
            print(f"  Error exploring menu items: {e}")

    def _capture_modals(self):
        """Check for and capture any modals or dialogs"""
        print("\n[Phase 3] Checking for modals/dialogs...")

        modal_selectors = [
            "[role='dialog']:visible",
            "[class*='modal']:visible",
            "[class*='dialog']:visible",
        ]

        for selector in modal_selectors:
            try:
                modals = self.page.locator(selector).all()
                if modals:
                    print(f"  Found {len(modals)} modal(s)")
                    for idx, modal in enumerate(modals[:2]):
                        if modal.is_visible():
                            step_name = f"03-modal-{idx+1}"
                            description = f"Modal/Dialog {idx+1}"
                            result = self.capture_screenshot(step_name, description)
                            if result:
                                self.captured_steps.append(result)
            except:
                continue

    def _capture_dialog_fields(self):
        """Capture all fields in an opened dialog/form"""
        print("\n  [Dialog] Exploring form fields...")

        try:
            # Wait for dialog to appear
            self.page.wait_for_timeout(1000)

            # Look for dialog container
            dialog_selectors = [
                "[role='dialog']",
                ".v-dialog--active",
                "[class*='modal']",
                "[class*='dialog']"
            ]

            for selector in dialog_selectors:
                try:
                    dialogs = self.page.locator(f"{selector}:visible").all()
                    if dialogs and len(dialogs) > 0:
                        dialog = dialogs[0]
                        print(f"  Found dialog with selector: {selector}")

                        # Capture all input fields in dialog
                        inputs = dialog.locator("input:visible, textarea:visible").all()
                        if inputs:
                            print(f"  Found {len(inputs)} input field(s) in dialog")

                        # Capture all select/dropdowns in dialog
                        selects = dialog.locator("select:visible, [role='combobox']:visible").all()
                        if selects:
                            print(f"  Found {len(selects)} dropdown(s) in dialog")
                            # Try to click first dropdown to see options
                            for idx, sel in enumerate(selects[:3]):
                                try:
                                    if sel.is_visible():
                                        sel.click(timeout=2000)
                                        self.page.wait_for_timeout(1000)
                                        step_name = f"02-dialog-dropdown-{idx+1}"
                                        description = f"Dialog dropdown {idx+1} opened"
                                        result = self.capture_screenshot(step_name, description)
                                        if result:
                                            self.captured_steps.append(result)
                                        # Press Escape to close dropdown
                                        self.page.keyboard.press("Escape")
                                        self.page.wait_for_timeout(500)
                                except:
                                    continue

                        # Capture all buttons in dialog
                        buttons = dialog.locator("button:visible").all()
                        if buttons:
                            print(f"  Found {len(buttons)} button(s) in dialog")

                        break  # Found dialog, no need to try other selectors
                except:
                    continue

        except Exception as e:
            print(f"  Could not explore dialog fields: {e}")

    def save_results(self, feature_name="feature"):
        """Save captured data to JSON file"""
        output_file = self.output_dir / f"{feature_name}_captured.json"

        result = {
            "feature_name": feature_name,
            "capture_date": datetime.now().isoformat(),
            "capture_mode": "automatic_v3_state_tracking",
            "total_steps": len(self.captured_steps),
            "steps": self.captured_steps
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"✓ Results saved to: {output_file}")
        print(f"✓ Screenshots saved to: {self.screenshots_dir}")

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
        description="Capture CAM feature with state tracking (V3)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First, log in and save auth state
  python auto_login_cam_v3.py --username admin --password your-password

  # Then capture the page
  python auto_browse_cam_v3.py \\
    --url https://cam.camrealtest.top/v3/analysis/reporting/routine \\
    --feature-name routine-report \\
    --auth-file .auth/state.json

  # Run in headless mode
  python auto_browse_cam_v3.py \\
    --url https://cam.camrealtest.top/v3/analysis/reporting/routine \\
    --feature-name routine-report \\
    --headless
        """
    )

    parser.add_argument(
        '--url',
        required=True,
        help='CAM feature URL to capture'
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

    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )

    args = parser.parse_args()

    # Create capture instance
    capture = CAMCaptureV3(
        auth_file=args.auth_file,
        output_dir=args.output,
        headless=args.headless
    )

    # Launch browser
    if not capture.launch_browser():
        sys.exit(1)

    try:
        # Run automatic capture
        captured_steps = capture.automatic_capture(target_url=args.url)

        if captured_steps:
            # Save results
            output_file = capture.save_results(args.feature_name)

            print("\n" + "="*60)
            print("NEXT STEPS")
            print("="*60)
            print(f"\n1. Review captured data: {output_file}")
            print(f"2. Review screenshots: {capture.screenshots_dir}")
            print(f"3. Use this data to generate CAM documentation")
            print("="*60 + "\n")
        else:
            print("\nNo steps captured.")

    except KeyboardInterrupt:
        print("\n\nCapture interrupted by user.")

    except Exception as e:
        print(f"\nError during capture: {e}")
        import traceback
        traceback.print_exc()

    finally:
        capture.close()


if __name__ == "__main__":
    main()

