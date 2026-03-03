#!/usr/bin/env python3
"""
CAM Browser Capture - Persistent Context Version

Uses Playwright's launchPersistentContext to:
- Launch Chrome with a dedicated user profile
- Preserve login state across runs
- Avoid CDP connection issues
- Work reliably in Claude Code environment

Usage:
    python auto_browse_cam_persistent.py --url <cam-url> --feature-name <name>
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


class CAMPersistentCapture:
    def __init__(self, profile_dir="/tmp/cam-chrome-profile", output_dir="captured_data"):
        self.profile_dir = Path(profile_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.screenshots_dir = self.output_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)

        self.playwright = None
        self.context = None
        self.page = None
        self.captured_steps = []
        self.step_counter = 1

    def launch_browser(self):
        """Launch Chrome with persistent context"""
        try:
            self.playwright = sync_playwright().start()

            # Launch persistent context with Chrome
            # userDataDir should be the root directory, not a profile subdirectory
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=False,  # Show browser window
                channel="chrome",  # Use system Chrome
                args=[
                    "--profile-directory=Default",  # Specify which profile to use
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--no-default-browser-check",
                ],
                viewport={"width": 1920, "height": 1080},
                proxy={"server": "http://localhost:7890"},  # VPN proxy configuration
            )

            # Get or create the first page
            if self.context.pages:
                self.page = self.context.pages[0]
            else:
                self.page = self.context.new_page()

            print(f"✓ Browser launched with profile: {self.profile_dir}")
            print(f"✓ Current page: {self.page.url}")
            return True

        except Exception as e:
            print(f"Error launching browser: {e}")
            return False

    def capture_screenshot(self, step_name: str, description: str) -> Dict[str, Any]:
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

        self.captured_steps.append(page_info)
        self.step_counter += 1

        return page_info

    def automatic_capture(self, target_url: str):
        """Automatically explore and capture the page"""
        print("\n" + "="*60)
        print("AUTOMATIC CAPTURE MODE - PERSISTENT CONTEXT")
        print("="*60)

        # Navigate to URL
        print(f"\nNavigating to: {target_url}")
        self.page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        self.page.wait_for_timeout(3000)  # Wait for page to fully load

        print(f"Current page: {self.page.url}")
        print(f"Page title: {self.page.title()}\n")

        # Step 1: Capture initial state
        self.capture_screenshot("01-initial-page", "Initial page load")

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

        # Look for common CAM UI patterns
        selectors_to_try = [
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
                            self.capture_screenshot(step_name, description)

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
                            self.capture_screenshot(step_name, description)
            except:
                continue

    def save_results(self, feature_name="feature"):
        """Save captured data to JSON file"""
        output_file = self.output_dir / f"{feature_name}_captured.json"

        result = {
            "feature_name": feature_name,
            "capture_date": datetime.now().isoformat(),
            "capture_mode": "automatic_persistent",
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
        if self.playwright:
            self.playwright.stop()


def main():
    parser = argparse.ArgumentParser(
        description="Capture CAM feature using persistent browser context",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python auto_browse_cam_persistent.py --url https://cam.cammaster.org/v3/analysis/reporting/routine --feature-name routine-report

First run:
  - Browser will open with a fresh profile
  - Log into CAM manually
  - Script will capture the page

Subsequent runs:
  - Browser will reuse the same profile (login preserved)
  - Script will automatically navigate and capture
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
        '--profile-dir',
        default='/tmp/cam-chrome-profile',
        help='Chrome profile directory (default: /tmp/cam-chrome-profile)'
    )

    parser.add_argument(
        '--output',
        default='captured_data',
        help='Output directory for captured data (default: captured_data)'
    )

    parser.add_argument(
        '--skip-login-prompt',
        action='store_true',
        help='Skip the login prompt and proceed directly to capture'
    )

    args = parser.parse_args()

    # Create capture instance
    capture = CAMPersistentCapture(
        profile_dir=args.profile_dir,
        output_dir=args.output
    )

    # Launch browser
    if not capture.launch_browser():
        sys.exit(1)

    try:
        # Check if we need to log in
        if not args.skip_login_prompt:
            current_url = capture.page.url
            if current_url == "about:blank" or "login" in current_url.lower():
                print("\n" + "="*60)
                print("FIRST TIME SETUP")
                print("="*60)
                print("\nPlease log into CAM in the browser window.")
                print("Once logged in, press ENTER to continue...")
                input()

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
