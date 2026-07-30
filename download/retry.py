import time
import random
import logging
from typing import Callable, Any, Tuple, Type

logger = logging.getLogger("downloader")

def retry_with_backoff(
    func: Callable[[], Any],
    retries: int = 3,
    base_delay: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Any:
    for attempt in range(1, retries + 1):
        try:
            return func()
        except exceptions as e:
            if attempt == retries:
                logger.error(f"Final attempt {attempt} failed: {e}")
                raise
            # Exponential backoff with jitter
            delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
            logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay:.2f} seconds...")
            time.sleep(delay)
