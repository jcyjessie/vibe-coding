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

    # Mock page with API response and locator
    class MockPage:
        class MockRequest:
            def get(self, url):
                class MockResponse:
                    status = 200
                return MockResponse()

        request = MockRequest()

        def locator(self, selector):
            class MockLocator:
                def is_visible(self, timeout=None):
                    return False  # Selectors fail, but API succeeds
            return MockLocator()

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


def test_login_validator_all_selectors_fail():
    """Test that validator returns False when all selectors fail"""
    validator = LoginValidator(
        home_selectors=[".nonexistent-1", ".nonexistent-2"]
    )

    # Mock page where no selectors are visible
    class MockPage:
        def locator(self, selector):
            class MockLocator:
                def is_visible(self, timeout=None):
                    return False
            return MockLocator()

    page = MockPage()
    assert not validator.verify_login_success(page)


def test_login_validator_api_failure():
    """Test that validator handles API check failure"""
    validator = LoginValidator(
        api_endpoint="/api/user/info",
        expected_status=200
    )

    # Mock page with API error
    class MockPage:
        class MockRequest:
            def get(self, url):
                class MockResponse:
                    status = 401  # Unauthorized
                return MockResponse()

        request = MockRequest()

        def locator(self, selector):
            class MockLocator:
                def is_visible(self, timeout=None):
                    return False
            return MockLocator()

    page = MockPage()
    assert not validator.verify_login_via_api(page)


def test_login_validator_combined_both_pass():
    """Test that combined mode requires both checks to pass"""
    validator = LoginValidator(
        home_selectors=[".user-menu"],
        api_endpoint="/api/user/info",
        require_both=True
    )

    # Mock page with both selector and API working
    class MockPage:
        class MockRequest:
            def get(self, url):
                class MockResponse:
                    status = 200
                return MockResponse()

        request = MockRequest()

        def locator(self, selector):
            class MockLocator:
                def is_visible(self, timeout=None):
                    return selector == ".user-menu"
            return MockLocator()

    page = MockPage()
    assert validator.verify_login_success(page)


def test_login_validator_combined_one_fails():
    """Test that combined mode fails if either check fails"""
    validator = LoginValidator(
        home_selectors=[".user-menu"],
        api_endpoint="/api/user/info",
        require_both=True
    )

    # Mock page with selector working but API failing
    class MockPage:
        class MockRequest:
            def get(self, url):
                class MockResponse:
                    status = 401
                return MockResponse()

        request = MockRequest()

        def locator(self, selector):
            class MockLocator:
                def is_visible(self, timeout=None):
                    return selector == ".user-menu"
            return MockLocator()

    page = MockPage()
    assert not validator.verify_login_success(page)


def test_login_validator_empty_selectors():
    """Test that empty home_selectors raises ValueError"""
    with pytest.raises(ValueError, match="home_selectors cannot be empty"):
        LoginValidator(home_selectors=[])


def test_login_validator_exception_handling():
    """Test that validator handles exceptions gracefully"""
    validator = LoginValidator(
        home_selectors=[".user-menu"]
    )

    # Mock page that raises exception
    class MockPage:
        def locator(self, selector):
            class MockLocator:
                def is_visible(self, timeout=None):
                    raise TimeoutError("Timeout waiting for selector")
            return MockLocator()

    page = MockPage()
    # Should return False instead of raising exception
    assert not validator.verify_login_success(page)

