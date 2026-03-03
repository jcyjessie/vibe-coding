#!/usr/bin/env python3
"""
CAM Auto Login Script

Automatically logs into CAM and saves the authentication state.
Similar to Playwright's global-setup pattern used in Kintsugi project.

Usage:
    python auto_login_cam.py --username admin --password your-password
"""

import argparse
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: Playwright is not installed.")
    print("Install it with: pip install playwright && playwright install chromium")
    sys.exit(1)


def auto_login(
    username,
    password,
    profile_dir="/tmp/cam-chrome-profile",
    base_url="https://cam.camrealtest.top"
):
    """
    Automatically log into CAM and save the session.

    Args:
        username: CAM username
        password: CAM password
        profile_dir: Chrome profile directory to save login state
        base_url: CAM base URL
    """
    profile_path = Path(profile_dir)
    profile_path.mkdir(parents=True, exist_ok=True)

    print(f"🔐 Starting auto-login to {base_url}...")
    print(f"📁 Profile directory: {profile_dir}")
    print(f"👤 Username: {username}")

    with sync_playwright() as p:
        # Launch browser with persistent context (saves login state automatically)
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=False,  # Show browser so you can see what's happening
            channel="chrome",
            args=[
                "--profile-directory=Default",
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
            ],
            viewport={"width": 1440, "height": 900},
            proxy={"server": "http://localhost:7890"},  # VPN proxy
        )

        # Get or create page
        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()

        try:
            # Navigate to login page
            print(f"\n📍 Navigating to {base_url}/login...")
            page.goto(f"{base_url}/login", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=10000)

            # Fill in credentials
            print("✍️  Filling in credentials...")
            page.fill("input[name='username']", username)
            page.fill("input[name='password']", password)

            # Click login button
            print("🔘 Clicking login button...")
            page.click("button:has-text('Log in')")

            # Wait for redirect to home page
            print("⏳ Waiting for login to complete...")
            page.wait_for_url("**/v3/home", timeout=30000)

            print("✅ Login successful!")
            print(f"📍 Current URL: {page.url}")

            # The login state is automatically saved in the persistent context
            print(f"\n✅ Login state saved to: {profile_dir}")
            print("🎉 You can now run the capture script with --skip-login-prompt")

        except Exception as e:
            print(f"\n❌ Login failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        finally:
            context.close()


def main():
    parser = argparse.ArgumentParser(
        description="Automatically log into CAM and save authentication state",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run auto-login
  python auto_login_cam.py --username admin --password your-password

  # Then run capture script
  python auto_browse_cam_persistent.py \\
    --url https://cam.camrealtest.top/v3/analysis/reporting/routine \\
    --feature-name routine-report \\
    --skip-login-prompt
        """
    )

    parser.add_argument(
        '--username',
        required=True,
        help='CAM username'
    )

    parser.add_argument(
        '--password',
        required=True,
        help='CAM password'
    )

    parser.add_argument(
        '--profile-dir',
        default='/tmp/cam-chrome-profile',
        help='Chrome profile directory to save login state (default: /tmp/cam-chrome-profile)'
    )

    parser.add_argument(
        '--base-url',
        default='https://cam.camrealtest.top',
        help='CAM base URL (default: https://cam.camrealtest.top)'
    )

    args = parser.parse_args()

    auto_login(
        username=args.username,
        password=args.password,
        profile_dir=args.profile_dir,
        base_url=args.base_url
    )


if __name__ == "__main__":
    main()
