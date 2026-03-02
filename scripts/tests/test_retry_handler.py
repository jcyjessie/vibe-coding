import pytest
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from retry_handler import RetryHandler, RetryableError


def test_retry_handler_initialization():
    handler = RetryHandler(max_retries=3, base_delay=0.1)
    assert handler.max_retries == 3
    assert handler.base_delay == 0.1


def test_successful_operation_no_retry():
    handler = RetryHandler(max_retries=3, base_delay=0.1)
    call_count = 0

    def successful_operation():
        nonlocal call_count
        call_count += 1
        return "success"

    result = handler.execute(successful_operation)
    assert result == "success"
    assert call_count == 1


def test_retry_on_retryable_error():
    handler = RetryHandler(max_retries=3, base_delay=0.1)
    call_count = 0

    def failing_then_success():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RetryableError("Temporary failure")
        return "success"

    result = handler.execute(failing_then_success)
    assert result == "success"
    assert call_count == 3


def test_max_retries_exceeded():
    handler = RetryHandler(max_retries=2, base_delay=0.1)
    call_count = 0

    def always_fails():
        nonlocal call_count
        call_count += 1
        raise RetryableError("Always fails")

    with pytest.raises(RetryableError):
        handler.execute(always_fails)

    assert call_count == 3
