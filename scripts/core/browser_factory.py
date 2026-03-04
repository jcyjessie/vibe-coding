#!/usr/bin/env python3
"""
Browser Factory - Unified browser setup for all CAM automation scripts.

Provides a single create_page() function that handles:
- Playwright lifecycle management
- Browser launch with consistent settings
- Context creation (with or without auth state)
- Page creation ready for automation

Usage:
    from core.browser_factory import create_page
    from core.config import RuntimeConfig

    # Using RuntimeConfig (recommended)
    cfg = load_config_from_env()
    page, cleanup = create_page(config=cfg, auth_file=cfg.auth_file)

    # Legacy usage (backward compatible)
    page, cleanup = create_page(auth_file=".auth/state.json")

    # Always call cleanup when done
    cleanup()
"""

from pathlib import Path
from typing import Tuple, Optional, Callable
import logging

try:
    from playwright.sync_api import sync_playwright, Page
except ImportError:
    raise ImportError(
        "Playwright is not installed. "
        "Install it with: pip install playwright && playwright install chromium"
    )

logger = logging.getLogger(__name__)


def create_page(
    auth_file: Optional[str] = None,
    headless: bool = False,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
    proxy_server: Optional[str] = "http://localhost:7890",
    channel: str = "chrome",
    config: Optional['RuntimeConfig'] = None
) -> Tuple[Page, Callable[[], None]]:
    """
    Create a Playwright page with consistent browser settings.

    Args:
        auth_file: Path to authentication state file (optional)
        headless: Run browser in headless mode
        viewport_width: Browser viewport width
        viewport_height: Browser viewport height
        proxy_server: Proxy server URL (None to disable)
        channel: Browser channel (chrome, chromium, msedge)
        config: RuntimeConfig object (overrides individual params if provided)

    Returns:
        Tuple of (page, cleanup_function)
        - page: Playwright Page object ready for automation
        - cleanup_function: Call this to close browser and stop playwright

    Raises:
        FileNotFoundError: If auth_file is specified but doesn't exist
    """
    # Use config if provided (overrides individual params)
    if config is not None:
        headless = config.headless
        viewport_width = config.viewport_width
        viewport_height = config.viewport_height
        proxy_server = config.proxy
        channel = config.channel

    # Validate auth file if provided
    if auth_file:
        auth_path = Path(auth_file)
        if not auth_path.exists():
            raise FileNotFoundError(
                f"Auth file not found: {auth_file}\n"
                "Please run 'cam_doc login' first to authenticate."
            )

    # Start playwright
    playwright = sync_playwright().start()

    # Launch browser with consistent settings
    launch_options = {
        "headless": headless,
        "channel": channel
    }

    # Add proxy if specified
    if proxy_server:
        launch_options["proxy"] = {"server": proxy_server}

    browser = playwright.chromium.launch(**launch_options)

    # Create context (with or without auth state)
    context_options = {
        "viewport": {"width": viewport_width, "height": viewport_height}
    }

    if auth_file:
        context_options["storage_state"] = str(auth_file)
        logger.info(f"Browser launched with auth state: {auth_file}")
    else:
        logger.info("Browser launched without auth state")

    context = browser.new_context(**context_options)

    # Create page
    page = context.new_page()

    # Define cleanup function
    def cleanup():
        """Close browser and stop playwright"""
        try:
            context.close()
        except Exception as e:
            logger.debug(f"Error closing context: {e}")

        try:
            browser.close()
        except Exception as e:
            logger.debug(f"Error closing browser: {e}")

        try:
            playwright.stop()
        except Exception as e:
            logger.debug(f"Error stopping playwright: {e}")

    return page, cleanup
