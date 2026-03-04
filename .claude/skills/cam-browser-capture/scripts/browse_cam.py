#!/usr/bin/env python3
"""
CAM Browser Automation Script

Connects to an already-logged-in Chrome browser and captures:
- Screenshots of each step
- UI element labels and text
- Page structure and navigation paths

Usage:
    1. Start Chrome with debugging port:
       chrome --remote-debugging-port=9222

    2. Manually log into CAM in that browser

    3. Run this script:
       python browse_cam.py --url <cam-feature-url>
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Error: Playwright is not installed.")
    print("Install it with: pip install playwright && playwright install chromium")
    sys.exit(1)


class CAMBrowserCapture:
    def __init__(self, debug_port=9222, output_dir="captured_data"):
        self.debug_port = debug_port
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.screenshots_dir = self.output_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)

        self.playwright = None
        self.browser = None
        self.page = None

    def connect(self):
        """Connect to existing Chrome browser with debugging port"""
        try:
            import urllib.request as _req, json as _json
            with _req.urlopen(f"http://localhost:{self.debug_port}/json/version") as r:
                ws_url = _json.loads(r.read())["webSocketDebuggerUrl"]
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.connect_over_cdp(ws_url)

            # Get the first available page or create new one
            if self.browser.contexts:
                context = self.browser.contexts[0]
                if context.pages:
                    self.page = context.pages[0]
                else:
                    self.page = context.new_page()
            else:
                print("Error: No browser context found. Make sure Chrome is running with --remote-debugging-port=9222")
                return False

            print(f"✓ Connected to Chrome browser (port {self.debug_port})")
            return True

        except Exception as e:
            print(f"Error connecting to browser: {e}")
            print("\nMake sure Chrome is running with:")
            print("  chrome --remote-debugging-port=9222")
            return False

    def capture_page_info(self, step_name="initial"):
        """Capture current page information"""
        if not self.page:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_filename = f"{step_name}_{timestamp}.png"
        screenshot_path = self.screenshots_dir / screenshot_filename

        # Take screenshot
        self.page.screenshot(path=str(screenshot_path), full_page=True)

        # Extract page information
        page_info = {
            "step_name": step_name,
            "url": self.page.url,
            "title": self.page.title(),
            "screenshot": str(screenshot_filename),
            "timestamp": timestamp
        }

        # Extract visible buttons
        try:
            buttons = self.page.locator("button:visible").all()
            page_info["buttons"] = [
                {
                    "text": btn.text_content().strip(),
                    "type": "button"
                }
                for btn in buttons[:20]  # Limit to first 20
                if btn.text_content().strip()
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
                for inp in inputs[:20]  # Limit to first 20
            ]
        except:
            page_info["input_fields"] = []

        # Extract headings
        try:
            headings = self.page.locator("h1, h2, h3").all()
            page_info["headings"] = [
                {
                    "level": h.evaluate("el => el.tagName"),
                    "text": h.text_content().strip()
                }
                for h in headings[:10]  # Limit to first 10
                if h.text_content().strip()
            ]
        except:
            page_info["headings"] = []

        print(f"✓ Captured: {step_name}")
        print(f"  - Screenshot: {screenshot_filename}")
        print(f"  - Buttons found: {len(page_info.get('buttons', []))}")
        print(f"  - Input fields found: {len(page_info.get('input_fields', []))}")

        return page_info

    def interactive_capture(self, initial_url=None):
        """Interactive mode: user performs actions, script captures each step"""
        if initial_url:
            print(f"\nNavigating to: {initial_url}")
            if self.page.url != initial_url:
                self.page.goto(initial_url, wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_timeout(2000)

        print("\n" + "="*60)
        print("INTERACTIVE CAPTURE MODE")
        print("="*60)
        print("\nInstructions:")
        print("  1. Perform actions in the browser (click, type, navigate)")
        print("  2. After each meaningful step, come back here")
        print("  3. Press ENTER to capture the current state")
        print("  4. Type a description for the step")
        print("  5. Type 'done' when finished")
        print("="*60 + "\n")

        captured_steps = []
        step_number = 1

        while True:
            input(f"\n[Step {step_number}] Press ENTER after performing an action in the browser (or type 'done' to finish): ")

            user_input = input("Describe what you just did (or 'done' to finish): ").strip()

            if user_input.lower() == 'done':
                break

            if not user_input:
                print("Please provide a description for this step.")
                continue

            # Capture current state
            step_name = f"step-{step_number}"
            page_info = self.capture_page_info(step_name)

            if page_info:
                page_info["description"] = user_input
                page_info["step_number"] = step_number
                captured_steps.append(page_info)
                step_number += 1

        return captured_steps

    def save_results(self, captured_steps, feature_name="feature"):
        """Save captured data to JSON file"""
        output_file = self.output_dir / f"{feature_name}_captured.json"

        result = {
            "feature_name": feature_name,
            "capture_date": datetime.now().isoformat(),
            "total_steps": len(captured_steps),
            "steps": captured_steps
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Results saved to: {output_file}")
        print(f"✓ Screenshots saved to: {self.screenshots_dir}")

        return output_file

    def close(self):
        """Clean up resources"""
        if self.playwright:
            self.playwright.stop()


def main():
    parser = argparse.ArgumentParser(
        description="Capture CAM feature workflow from browser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start Chrome with debugging (run this first in a separate terminal):
  chrome --remote-debugging-port=9222

  # Then run the capture script:
  python browse_cam.py --url https://cam.example.com/portfolio-snapshot

  # Or just connect to current page:
  python browse_cam.py
        """
    )

    parser.add_argument(
        '--url',
        help='CAM feature URL to navigate to (optional, uses current page if not provided)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=9222,
        help='Chrome debugging port (default: 9222)'
    )

    parser.add_argument(
        '--output',
        default='captured_data',
        help='Output directory for captured data (default: captured_data)'
    )

    parser.add_argument(
        '--feature-name',
        default='feature',
        help='Feature name for output files (default: feature)'
    )

    args = parser.parse_args()

    # Create capture instance
    capture = CAMBrowserCapture(
        debug_port=args.port,
        output_dir=args.output
    )

    # Connect to browser
    if not capture.connect():
        sys.exit(1)

    try:
        # Run interactive capture
        captured_steps = capture.interactive_capture(initial_url=args.url)

        if captured_steps:
            # Save results
            output_file = capture.save_results(captured_steps, args.feature_name)

            print("\n" + "="*60)
            print("CAPTURE COMPLETE")
            print("="*60)
            print(f"\nCaptured {len(captured_steps)} steps")
            print(f"\nNext steps:")
            print(f"  1. Review the captured data: {output_file}")
            print(f"  2. Use this data to generate CAM documentation")
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
