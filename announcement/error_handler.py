import functools
import time
import logging
from django.conf import settings
from telegram.error import TelegramError

class RetryableError(Exception):
    """Qayta urinish mumkin bo'lgan xatolar"""
    pass

def with_retry(max_retries=3, delay=1):
    """Retry decorator"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except RetryableError as e:
                    retries += 1
                    if retries == max_retries:
                        raise
                    time.sleep(delay * (2 ** (retries - 1)))  # Exponential backoff
                    logging.warning(f"Retry {retries}/{max_retries} for {func.__name__}: {str(e)}")
            return None
        return wrapper
    return decorator

class ErrorHandler:
    @staticmethod
    def handle_telegram_error(func):
        """Telegram xatolarini handling qilish"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TelegramError as e:
                if "Too Many Requests" in str(e):
                    raise RetryableError("Rate limit exceeded")
                elif "Bad Request" in str(e):
                    logging.error(f"Bad request: {str(e)}")
                    raise
                elif "Network" in str(e):
                    raise RetryableError("Network error")
                else:
                    logging.error(f"Unexpected Telegram error: {str(e)}")
                    raise
        return wrapper 