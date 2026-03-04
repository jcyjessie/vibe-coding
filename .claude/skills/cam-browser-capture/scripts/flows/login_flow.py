#!/usr/bin/env python3
"""
Login Flow - Extracted from auto_login_cam_v3.py

Provides reusable login functionality with strong signal validation.
"""

import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

from retry_handler import RetryableError

logger = logging.getLogger(__name__)


@dataclass
class LoginValidator:
    """
    Strong signal validation for login success.

    Provides multiple validation strategies:
    1. Home selector check (wait for stable UI element)
    2. API endpoint check (verify authenticated API call)
    3. Combined (both must pass)
    """
    home_selectors: List[str] = None
    api_endpoint: Optional[str] = None
    expected_status: int = 200
    require_both: bool = False
    timeout: int = 10000  # 10 seconds

    def __post_init__(self):
        if self.home_selectors is None:
            self.home_selectors = [
                ".user-menu",
                "[data-testid='user-profile']",
                ".account-dropdown"
            ]

        # Validate that home_selectors is not empty
        if not self.home_selectors:
            raise ValueError("home_selectors cannot be empty")

        if self.require_both and not self.api_endpoint:
            raise ValueError("require_both=True requires api_endpoint to be set")

    @property
    def validation_strategy(self) -> str:
        """Get current validation strategy"""
        if self.require_both:
            return "combined"
        elif self.api_endpoint:
            return "api_primary"
        else:
            return "selector_only"

    def verify_login_success(self, page) -> bool:
        """
        Verify login success using configured strategy.

        Args:
            page: Playwright page object

        Returns:
            True if login verified, False otherwise
        """
        selector_valid = self._check_home_selectors(page)

        if self.api_endpoint:
            api_valid = self.verify_login_via_api(page)

            if self.require_both:
                return selector_valid and api_valid
            else:
                # API check is primary, selector is fallback
                return api_valid or selector_valid

        return selector_valid

    def _check_home_selectors(self, page) -> bool:
        """Check if any home selector is visible"""
        for selector in self.home_selectors:
            try:
                locator = page.locator(selector)
                if locator.is_visible(timeout=self.timeout):
                    logger.info(f"✓ Login verified: found home selector '{selector}'")
                    return True
            except (TimeoutError, Exception) as e:
                logger.debug(f"  Selector '{selector}' not found: {e}")
                continue

        logger.error("✗ Login verification failed: no home selectors found")
        return False

    def verify_login_via_api(self, page) -> bool:
        """
        Verify login by calling authenticated API endpoint.

        Args:
            page: Playwright page object

        Returns:
            True if API returns expected status, False otherwise
        """
        try:
            # Make API request using page context (includes cookies)
            response = page.request.get(self.api_endpoint)

            if response.status == self.expected_status:
                logger.info(f"✓ Login verified: API {self.api_endpoint} returned {response.status}")
                return True
            else:
                logger.error(f"✗ API check failed: expected {self.expected_status}, got {response.status}")
                return False

        except (AttributeError, TimeoutError, Exception) as e:
            logger.error(f"✗ API check failed: {e}")
            return False


def verify_login(page) -> bool:
    """
    Verify login success with strong signal validation.

    Args:
        page: Playwright page object

    Returns:
        True if login verified, False otherwise
    """
    logger.info("\n=== Verifying Login Success ===")

    # Use LoginValidator with default selectors
    validator = LoginValidator()

    return validator.verify_login_success(page)


def perform_login_flow(page, username: str, password: str, base_url: str) -> None:
    """
    Execute the login flow on a given page.

    Args:
        page: Playwright page object
        username: CAM username
        password: CAM password
        base_url: CAM base URL

    Raises:
        RetryableError: If login fails
    """
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

    # Wait for redirect to home page (or any v3 page)
    logger.info("Waiting for login to complete...")
    try:
        page.wait_for_url("**/v3/**", timeout=10000)
    except:
        # Check if we're already at v3
        if "/v3" not in page.url:
            logger.warning("Not redirected to v3 page")
            raise RetryableError("Login did not redirect to v3 page")

    # Use LoginValidator for robust verification
    if not verify_login(page):
        raise RetryableError("Login verification failed - no home selectors found")

    logger.info("Login successful!")
    logger.info(f"Current URL: {page.url}")


def save_auth_state(page, auth_file: str) -> None:
    """
    Save authentication state to file.

    Args:
        page: Playwright page object
        auth_file: Path to save authentication state
    """
    auth_path = Path(auth_file)
    auth_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Saving authentication state...")
    page.context.storage_state(path=str(auth_path))

    logger.info(f"Auth state saved to: {auth_file}")
    logger.info("You can now run the capture script with this auth state")

