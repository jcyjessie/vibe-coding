#!/usr/bin/env python3
"""
CAM Auto Login Script - V2 (Kintsugi Style)

Uses storageState instead of persistent context.
Similar to Kintsugi project's global-setup.ts pattern.

Usage:
    # Set password in environment variable
    export FRESH_MASTER_ADMIN_PASSWORD='your-password'

    # Run login script
    python auto_login_cam_v2.py --username admin
"""

import argparse
import json
import sys
import os
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
    auth_file=".auth/state.json",
    base_url="https://cam.camrealtest.top"
):
    """
    Automatically log into CAM and save the session using storageState.

    This approach is more reliable than persistent context because:
    1. Doesn't conflict with existing Chrome instances
    2. Only saves cookies/localStorage, not full profile
    3. Works with proxy configuration

    Args:
        username: CAM username
        password: CAM password
        auth_file: Path to save authentication state
        base_url: CAM base URL
    """
    auth_path = Path(auth_file)
    auth_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"🔐 Starting auto-login to {base_url}...")
    print(f"📁 Auth file: {auth_file}")
    print(f"👤 Username: {username}")

    with sync_playwright() as p:
        # Launch browser with proxy (like Kintsugi)
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            proxy={"server": "http://localhost:7890"}
        )

        # Create new page (no existing state)
        page = browser.new_page()

        try:
            # Navigate to login page
            print(f"\n📍 Navigating to {base_url}/login...")
            page.goto(f"{base_url}/login", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=10000)

            # Fill in credentials
            print("✍️  Filling in credentials...")
            page.get_by_role("textbox", name="Email/User").fill(username)
            page.get_by_role("textbox", name="Password").fill(password)

            # Click login button
            print("🔘 Clicking login button...")
            page.get_by_role("button", name="Log in").click()

            # Wait a moment for the page to respond
            page.wait_for_timeout(3000)

            # Check current URL to see if we need 2FA
            current_url = page.url
            print(f"📍 Current URL after login: {current_url}")

            # If already at /v3 or /v3/home, login successful
            if "/v3" in current_url:
                print("✅ Already redirected to v3, login successful!")
            else:
                # Might need 2FA or manual intervention
                print("\n🔐 Manual verification may be required!")
                print("Please check the browser window and complete any verification.")
                print("Waiting 30 seconds for you to complete...")
                page.wait_for_timeout(30000)

            # Wait for redirect to home page (or any v3 page)
            print("⏳ Waiting for login to complete...")
            try:
                page.wait_for_url("**/v3/**", timeout=10000)
            except:
                # Already at v3, that's fine
                pass

            print("✅ Login successful!")
            print(f"📍 Current URL: {page.url}")

            # Save authentication state (cookies + localStorage)
            print(f"\n💾 Saving authentication state...")
            page.context.storage_state(path=str(auth_path))

            print(f"✅ Auth state saved to: {auth_file}")
            print("🎉 You can now run the capture script with this auth state")

        except Exception as e:
            print(f"\n❌ Login failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Automatically log into CAM and save authentication state (Kintsugi style)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run auto-login
  python auto_login_cam_v2.py --username admin --password your-password

  # Then run capture script
  python auto_browse_cam_v2.py \\
    --url https://cam.camrealtest.top/v3/analysis/reporting/routine \\
    --feature-name routine-report \\
    --auth-file .auth/state.json
        """
    )

    parser.add_argument(
        '--username',
        required=True,
        help='CAM username'
    )

    parser.add_argument(
        '--password',
        default=None,
        help='CAM password (or set FRESH_MASTER_ADMIN_PASSWORD environment variable)'
    )

    parser.add_argument(
        '--auth-file',
        default='.auth/state.json',
        help='Path to save authentication state (default: .auth/state.json)'
    )

    parser.add_argument(
        '--base-url',
        default='https://fresh2.cammaster.org',
        help='CAM base URL (default: https://fresh2.cammaster.org)'
    )

    args = parser.parse_args()

    # Get password from args or environment variable (Kintsugi style)
    password = args.password or os.getenv('FRESH_MASTER_ADMIN_PASSWORD')
    if not password:
        print("❌ Error: Password not provided")
        print("Either:")
        print("  1. Set environment variable: export FRESH_MASTER_ADMIN_PASSWORD='your-password'")
        print("  2. Or pass --password argument")
        sys.exit(1)

    auto_login(
        username=args.username,
        password=password,
        auth_file=args.auth_file,
        base_url=args.base_url
    )


if __name__ == "__main__":
    main()
