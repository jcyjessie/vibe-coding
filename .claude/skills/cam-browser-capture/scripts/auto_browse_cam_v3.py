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
from core.browser_factory import create_page
from core.artifacts import StepRecorder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CAMCaptureV3:
    def __init__(self, auth_file=".auth/state.json", output_dir="captured_data", headless=False):
        self.auth_file = Path(auth_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.page = None
        self.cleanup = None
        self.headless = headless

        # 初始化状态跟踪模块
        self.state_tracker = StateTracker()
        self.selector_engine = SelectorEngine()
        self.retry_handler = RetryHandler(max_retries=3, base_delay=1.0)

        # Note: StepRecorder will be initialized in automatic_capture() with feature_name
        self.recorder = None

    def launch_browser(self):
        """Launch Chrome with storageState (Kintsugi style)"""
        try:
            # Use BrowserFactory to create page
            self.page, self.cleanup = create_page(
                auth_file=str(self.auth_file),
                headless=self.headless
            )

            logger.info(f"Browser launched with auth state: {self.auth_file}")
            return True

        except Exception as e:
            logger.error(f"Error launching browser: {e}")
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
            except Exception as e:
                logger.debug(f"Failed to extract visible buttons: {e}")

            # 提取可见输入框
            try:
                inputs = self.page.locator("input:visible, textarea:visible").all()
                state["visible_inputs"] = [
                    inp.get_attribute("placeholder") or inp.get_attribute("name") or ""
                    for inp in inputs[:30]
                ]
            except Exception as e:
                logger.debug(f"Failed to extract visible inputs: {e}")

            # 提取可见下拉框
            try:
                dropdowns = self.page.locator("select:visible, [role='combobox']:visible").all()
                state["visible_dropdowns"] = [
                    sel.get_attribute("name") or sel.get_attribute("aria-label") or ""
                    for sel in dropdowns[:20]
                ]
            except Exception as e:
                logger.debug(f"Failed to extract visible dropdowns: {e}")

            return state

        except Exception as e:
            logger.error(f"Error detecting state: {e}")
            return {}

    def capture_screenshot(self, step_name: str, description: str) -> Optional[Dict[str, Any]]:
        """Capture screenshot and page info, skip if duplicate state"""
        # 检测当前状态
        current_state = self._detect_state_change()

        # 检查是否为重复状态
        fingerprint = self.state_tracker.generate_fingerprint(current_state)
        if self.state_tracker.has_visited_state(fingerprint):
            logger.info(f"Skipping duplicate state: {step_name}")
            return None

        # 记录新状态
        self.state_tracker.mark_state_visited(fingerprint)

        # Extract page information for extra_data
        page_info = {}

        # Extract visible buttons
        try:
            buttons = self.page.locator("button:visible").all()
            page_info["buttons"] = [
                btn.text_content().strip()
                for btn in buttons[:30]
                if btn.text_content() and btn.text_content().strip()
            ]
        except Exception as e:
            logger.debug(f"Failed to extract buttons: {e}")
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
        except Exception as e:
            logger.debug(f"Failed to extract input fields: {e}")
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
        except Exception as e:
            logger.debug(f"Failed to extract dropdowns: {e}")
            page_info["dropdowns"] = []

        logger.info(f"  Buttons: {len(page_info.get('buttons', []))}, Inputs: {len(page_info.get('input_fields', []))}, Dropdowns: {len(page_info.get('dropdowns', []))}")

        # Use StepRecorder to capture
        return self.recorder.capture_step(
            page=self.page,
            step_name=step_name,
            description=description,
            extra_data=page_info
        )

    def automatic_capture(self, target_url: str, feature_name: str = "feature"):
        """Automatically explore and capture the page"""
        logger.info("=" * 60)
        logger.info("AUTOMATIC CAPTURE MODE - V3 (STATE TRACKING)")
        logger.info("=" * 60)

        # Initialize StepRecorder with feature name
        self.recorder = StepRecorder(output_dir=str(self.output_dir), feature_name=feature_name)

        # Navigate to URL
        logger.info(f"Navigating to: {target_url}")
        self.page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        self.page.wait_for_timeout(3000)  # Wait for page to fully load

        logger.info(f"Current page: {self.page.url}")
        logger.info(f"Page title: {self.page.title()}")

        # Step 1: Capture initial state
        result = self.capture_screenshot("01-initial-page", "Initial page load")

        # Step 2: Find and capture interactive elements
        self._capture_interactive_elements()

        # Step 3: Capture any modals or dialogs
        self._capture_modals()

        logger.info("=" * 60)
        logger.info(f"CAPTURE COMPLETE - {self.recorder.get_step_count()} steps captured")
        logger.info("=" * 60)

        return self.recorder.captured_steps

    def _capture_interactive_elements(self):
        """Find and interact with dropdowns, buttons, date pickers"""
        logger.info("[Phase 2] Exploring interactive elements...")

        # Priority 1: Look for "New" button first (common in CAM for creating configs)
        logger.info("[Priority] Looking for 'New' button...")
        try:
            # Use selector engine for robust i18n-safe selection
            new_button_selectors = self.selector_engine.get_fallback_selectors(
                element_type="button",
                aria_label="New",
                text="New"
            )

            new_buttons = []
            for selector in new_button_selectors:
                try:
                    buttons = self.page.locator(f"{selector}:visible").all()
                    if buttons:
                        new_buttons = buttons
                        logger.info(f"Found {len(new_buttons)} 'New' button(s) using selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            if new_buttons:
                for idx, btn in enumerate(new_buttons[:1]):  # Only click first one
                    try:
                        if btn.is_visible():
                            logger.info("Clicking 'New' button...")
                            btn.click(timeout=3000)
                            self.page.wait_for_timeout(2000)

                            # Capture the opened dialog/form
                            step_name = f"02-new-button-clicked"
                            description = "Clicked 'New' button - configuration form opened"
                            self.capture_screenshot(step_name, description)

                            # Try to capture form fields in the dialog
                            self._capture_dialog_fields()

                            # Close dialog if there's a close button
                            try:
                                close_button_selectors = self.selector_engine.get_fallback_selectors(
                                    element_type="button",
                                    aria_label="Cancel",
                                    text="Cancel"
                                )
                                for selector in close_button_selectors:
                                    try:
                                        close_btns = self.page.locator(f"{selector}:visible").all()
                                        if close_btns:
                                            close_btns[0].click(timeout=2000)
                                            self.page.wait_for_timeout(1000)
                                            logger.info("Closed dialog")
                                            break
                                    except Exception as e:
                                        logger.debug(f"Close button selector {selector} failed: {e}")
                                        continue
                            except Exception as e:
                                logger.debug(f"Could not close dialog: {e}")
                    except (PlaywrightTimeout, Exception) as e:
                        logger.warning(f"Could not interact with 'New' button: {e}")
                        continue
        except Exception as e:
            logger.info(f"No 'New' button found or error: {e}")

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
                    logger.info(f"Found {len(elements)} {element_type}(s)")

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
                            self.capture_screenshot(step_name, description)

                            # If it's a menu button, try to explore menu items
                            if "menu" in element_type:
                                self._explore_menu_items(element_type, idx)

                            # Click elsewhere to close (if it's a dropdown)
                            if "dropdown" in element_type or "picker" in element_type:
                                try:
                                    self.page.keyboard.press("Escape")
                                    self.page.wait_for_timeout(500)
                                except Exception as e:
                                    logger.debug(f"Could not close dropdown: {e}")

                            break  # Only interact with first visible element of each type

                        except (PlaywrightTimeout, Exception) as e:
                            logger.debug(f"Element not clickable: {e}")
                            continue

            except Exception as e:
                logger.debug(f"Selector {selector} did not match: {e}")
                continue

    def _explore_menu_items(self, menu_type: str, menu_idx: int):
        """After opening a menu, try to click each menu item to capture workflows"""
        logger.info("[Menu] Exploring menu items...")

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
                        logger.info(f"Found {len(menu_items)} menu item(s) using selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Menu item selector {selector} failed: {e}")
                    continue

            if not menu_items:
                logger.info("No menu items found")
                return

            # Try to click each menu item
            for item_idx, item in enumerate(menu_items[:5]):  # Limit to first 5 items
                try:
                    if not item.is_visible():
                        continue

                    # Get menu item text
                    item_text = item.text_content().strip() if item.text_content() else f"item-{item_idx+1}"
                    logger.info(f"Clicking menu item: {item_text}")

                    # Click the menu item
                    item.click(timeout=2000)
                    self.page.wait_for_timeout(1500)

                    # Capture the result (could be a dialog, confirmation, or action)
                    step_name = f"03-{menu_type.replace(' ', '-')}-{menu_idx+1}-{item_text.lower().replace(' ', '-')}"
                    description = f"Clicked menu item: {item_text}"
                    self.capture_screenshot(step_name, description)

                    # Check if a dialog appeared and capture its fields
                    try:
                        dialog_visible = self.page.locator("[role='dialog']:visible, .v-dialog--active:visible").count() > 0
                        if dialog_visible:
                            logger.info(f"Dialog appeared after clicking '{item_text}'")
                            self._capture_dialog_fields()

                            # Close the dialog
                            close_button_selectors = self.selector_engine.get_fallback_selectors(
                                element_type="button",
                                aria_label="Cancel",
                                text="Cancel"
                            )
                            for selector in close_button_selectors:
                                try:
                                    close_buttons = self.page.locator(f"{selector}:visible").all()
                                    if close_buttons:
                                        close_buttons[0].click(timeout=2000)
                                        self.page.wait_for_timeout(1000)
                                        logger.info("Closed dialog")
                                        break
                                except Exception as e:
                                    logger.debug(f"Close button selector {selector} failed: {e}")
                                    continue
                    except Exception as e:
                        logger.debug(f"Could not check for dialog: {e}")

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
                                            logger.info("Re-opened menu for next item")
                                            break
                                except Exception as e:
                                    logger.debug(f"Could not re-open menu: {e}")
                                    continue
                    except Exception as e:
                        logger.debug(f"Could not re-open menu: {e}")

                except (PlaywrightTimeout, Exception) as e:
                    logger.warning(f"Could not interact with menu item: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error exploring menu items: {e}")

    def _capture_modals(self):
        """Check for and capture any modals or dialogs"""
        logger.info("[Phase 3] Checking for modals/dialogs...")

        modal_selectors = [
            "[role='dialog']:visible",
            "[class*='modal']:visible",
            "[class*='dialog']:visible",
        ]

        for selector in modal_selectors:
            try:
                modals = self.page.locator(selector).all()
                if modals:
                    logger.info(f"Found {len(modals)} modal(s)")
                    for idx, modal in enumerate(modals[:2]):
                        if modal.is_visible():
                            step_name = f"03-modal-{idx+1}"
                            description = f"Modal/Dialog {idx+1}"
                            self.capture_screenshot(step_name, description)
            except Exception as e:
                logger.debug(f"Modal selector {selector} failed: {e}")
                continue

    def _capture_dialog_fields(self):
        """Capture all fields in an opened dialog/form"""
        logger.info("[Dialog] Exploring form fields...")

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
                        logger.info(f"Found dialog with selector: {selector}")

                        # Capture all input fields in dialog
                        inputs = dialog.locator("input:visible, textarea:visible").all()
                        if inputs:
                            logger.info(f"Found {len(inputs)} input field(s) in dialog")

                        # Capture all select/dropdowns in dialog
                        selects = dialog.locator("select:visible, [role='combobox']:visible").all()
                        if selects:
                            logger.info(f"Found {len(selects)} dropdown(s) in dialog")
                            # Try to click first dropdown to see options
                            for idx, sel in enumerate(selects[:3]):
                                try:
                                    if sel.is_visible():
                                        sel.click(timeout=2000)
                                        self.page.wait_for_timeout(1000)
                                        step_name = f"02-dialog-dropdown-{idx+1}"
                                        description = f"Dialog dropdown {idx+1} opened"
                                        self.capture_screenshot(step_name, description)
                                        # Press Escape to close dropdown
                                        self.page.keyboard.press("Escape")
                                        self.page.wait_for_timeout(500)
                                except (PlaywrightTimeout, Exception) as e:
                                    logger.debug(f"Could not interact with dropdown: {e}")
                                    continue

                        # Capture all buttons in dialog
                        buttons = dialog.locator("button:visible").all()
                        if buttons:
                            logger.info(f"Found {len(buttons)} button(s) in dialog")

                        break  # Found dialog, no need to try other selectors
                except Exception as e:
                    logger.debug(f"Dialog selector {selector} failed: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Could not explore dialog fields: {e}")

    def save_results(self):
        """Save captured data to JSON file"""
        return self.recorder.save_results(capture_mode="automatic_v3_state_tracking")

    def close(self):
        """Clean up resources"""
        if self.cleanup:
            self.cleanup()


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
        captured_steps = capture.automatic_capture(target_url=args.url, feature_name=args.feature_name)

        if captured_steps:
            # Save results
            output_file = capture.save_results()

            logger.info("=" * 60)
            logger.info("NEXT STEPS")
            logger.info("=" * 60)
            logger.info(f"1. Review captured data: {output_file}")
            logger.info(f"2. Review screenshots: {capture.recorder.screenshots_dir}")
            logger.info(f"3. Use this data to generate CAM documentation")
            logger.info("=" * 60)
        else:
            logger.warning("No steps captured.")

    except KeyboardInterrupt:
        logger.info("Capture interrupted by user.")

    except Exception as e:
        logger.error(f"Error during capture: {e}")
        import traceback
        traceback.print_exc()

    finally:
        capture.close()


if __name__ == "__main__":
    main()

