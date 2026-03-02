#!/usr/bin/env python3
"""
CAM Auto Login Script - V3 (With Retry and Headless Support)

Uses storageState instead of persistent context.
Similar to Kintsugi project's global-setup.ts pattern.
Adds retry mechanism and headless mode for CI/CD compatibility.

Usage:
    # Set password in environment variable
    export FRESH_MASTER_ADMIN_PASSWORD='your-password'

    # Run login script (headless mode)
    python auto_login_cam_v3.py --username admin --headless

    # Run login script (headed mode for debugging)
    python auto_login_cam_v3.py --username admin
"""

import argparse
import json
import sys
import os
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    logger.error("Playwright is not installed.")
    logger.error("Install it with: pip install playwright && playwright install chromium")
    sys.exit(1)

from retry_handler import RetryHandler, RetryableError


def auto_login(
    username,
    password,
    auth_file=".auth/state.json",
    base_url="https://fresh2.cammaster.org",
    headless=False
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
        base_url: CAM base URL (default: https://fresh2.cammaster.org)
        headless: Run browser in headless mode (default: False)
    """
    auth_path = Path(auth_file)
    auth_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting auto-login to {base_url}...")
    logger.info(f"Auth file: {auth_file}")
    logger.info(f"Username: {username}")
    logger.info(f"Headless mode: {headless}")

    # 定义登录操作（用于重试）
    def perform_login():
        with sync_playwright() as p:
            # Launch browser with proxy (like Kintsugi)
            browser = p.chromium.launch(
                headless=headless,
                channel="chrome",
                proxy={"server": "http://localhost:7890"}
            )

            # Create new page (no existing state)
            page = browser.new_page()

            try:
                # Navigate to login page
                logger.info(f"Navigating to {base_url}/login...")
                page.goto(f"{base_url}/login", timeout=30000)
                page.wait_for_load_state("networkidle", timeout=10000)

                # Fill in credentials
                logger.info("Filling in credentials...")
                page.get_by_role("textbox", name="Email/User").fill(username)
                page.get_by_role("textbox", name="Password").fill(password)

                # Click login button
                logger.info("Clicking login button...")
                page.get_by_role("button", name="Log in").click()

                # Wait a moment for the page to respond
                page.wait_for_timeout(3000)

                # Check for error messages
                current_url = page.url
                logger.info(f"Current URL after login: {current_url}")

                # Check if there's an error message on the page
                try:
                    error_element = page.locator(".ant-message-error, .error-message, [class*='error']").first
                    if error_element.is_visible(timeout=2000):
                        error_text = error_element.text_content()
                        logger.error(f"Login error detected: {error_text}")
                        raise RetryableError(f"Login failed with error: {error_text}")
                except:
                    # No error message found, continue
                    pass

                # If already at /v3 or /v3/home, login successful
                if "/v3" in current_url:
                    logger.info("Already redirected to v3, login successful!")
                else:
                    # Might need 2FA or manual intervention
                    if not headless:
                        logger.info("Manual verification may be required!")
                        logger.info("Please check the browser window and complete any verification.")
                        logger.info("Waiting 30 seconds for you to complete...")
                        page.wait_for_timeout(30000)
                    else:
                        logger.warning("Not redirected to v3 and running in headless mode")
                        raise RetryableError("Login did not redirect to v3 page")

                # Wait for redirect to home page (or any v3 page)
                logger.info("Waiting for login to complete...")
                try:
                    page.wait_for_url("**/v3/**", timeout=10000)
                except:
                    # Check if we're already at v3
                    if "/v3" not in page.url:
                        raise RetryableError("Failed to reach v3 page after login")

                logger.info("Login successful!")
                logger.info(f"Current URL: {page.url}")

                # Save authentication state (cookies + localStorage)
                logger.info("Saving authentication state...")
                page.context.storage_state(path=str(auth_path))

                logger.info(f"Auth state saved to: {auth_file}")
                logger.info("You can now run the capture script with this auth state")

            except RetryableError:
                # Re-raise retryable errors
                raise
            except Exception as e:
                logger.error(f"Login failed: {e}")
                import traceback
                traceback.print_exc()
                raise RetryableError(f"Login operation failed: {e}")

            finally:
                browser.close()

    # 使用重试处理器执行登录
    retry_handler = RetryHandler(max_retries=3, base_delay=2.0)
    try:
        retry_handler.execute(perform_login)
    except RetryableError as e:
        logger.error(f"Login failed after all retries: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Automatically log into CAM and save authentication state (V3 with retry and headless)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run auto-login in headless mode
  python auto_login_cam_v3.py --username admin --password your-password --headless

  # Run auto-login in headed mode (for debugging)
  python auto_login_cam_v3.py --username admin --password your-password

  # Then run capture script
  python auto_browse_cam_v3.py \\
    --url https://fresh2.cammaster.org/v3/analysis/reporting/routine \\
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

    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (default: False)'
    )

    args = parser.parse_args()

    # Get password from args or environment variable (Kintsugi style)
    password = args.password or os.getenv('FRESH_MASTER_ADMIN_PASSWORD')
    if not password:
        logger.error("Password not provided")
        logger.error("Either:")
        logger.error("  1. Set environment variable: export FRESH_MASTER_ADMIN_PASSWORD='your-password'")
        logger.error("  2. Or pass --password argument")
        sys.exit(1)

    auto_login(
        username=args.username,
        password=password,
        auth_file=args.auth_file,
        base_url=args.base_url,
        headless=args.headless
    )


if __name__ == "__main__":
    main()
