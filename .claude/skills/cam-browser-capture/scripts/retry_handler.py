import time
import logging
from typing import Callable, TypeVar

T = TypeVar('T')
logger = logging.getLogger(__name__)


class RetryableError(Exception):
    """Exception that indicates operation should be retried"""
    pass


class RetryHandler:
    """Handles retry logic with exponential backoff"""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    def execute(self, operation: Callable[[], T]) -> T:
        """Execute operation with retry logic"""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return operation()
            except RetryableError as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"Max retries ({self.max_retries}) exceeded")

        raise last_exception
