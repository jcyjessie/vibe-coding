#!/usr/bin/env python3
"""
Tests for auto_login_cam_v3.py
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from auto_login_cam_v3 import LoginValidator


def test_login_validator_home_selector():
    """Test that login validator checks for stable home selector"""
    validator = LoginValidator(
        home_selectors=[".user-menu", "[data-testid='user-profile']"]
    )

    # Mock page with home selector
    class MockPage:
        def locator(self, selector):
            class MockLocator:
                def is_visible(self, timeout=None):
                    return selector == ".user-menu"
            return MockLocator()

    page = MockPage()
    assert validator.verify_login_success(page)


def test_login_validator_api_check():
    """Test that login validator can verify via API"""
    validator = LoginValidator(
        api_endpoint="/api/user/info",
        expected_status=200
    )

    # Mock page with API response
    class MockPage:
        class MockRequest:
            def get(self, url):
                class MockResponse:
                    status = 200
                return MockResponse()

        request = MockRequest()

    page = MockPage()
    assert validator.verify_login_via_api(page)


def test_login_validator_combined():
    """Test that validator uses both selector and API"""
    validator = LoginValidator(
        home_selectors=[".user-menu"],
        api_endpoint="/api/user/info",
        require_both=True
    )

    # Should require both checks to pass
    assert validator.validation_strategy == "combined"
