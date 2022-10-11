from abc import ABC
from datetime import datetime, timedelta

from django.conf import settings


class LimiterAbstractClass(ABC):
    # All limiters should implement the two following methods.

    def set_new_get_code_time(self, brand_slug: str, user: str):
        # The user has gotten new code, process and store the new time.
        raise NotImplementedError()

    def can_user_get_discount_code(self, brand_slug: str) -> bool:
        # Should user be able to get another code according to
        # The rules of limiting?
        raise NotImplementedError()


class SimpleInMemoryLimiter(LimiterAbstractClass):
    # This for the purpose of demonstrating the idea.
    # This class is not persistant, restart or crash would cause loss of data.
    # If the application is run by multiple processes, this doesnt work.
    # In that case a shared memory must be used, like a shared redis.

    def __init__(self, min_passed_time: timedelta):
        # {username: {brand: last_time, brand2: last_time2, ...}}
        self._last_get_code_time = {}

        self.min_passed_time = min_passed_time

    def set_new_get_code_time(self, brand_slug: str, username: str):
        if username not in self._last_get_code_time:
            self._last_get_code_time[username] = {}
        self._last_get_code_time[username][brand_slug] = datetime.now()

        return

    def can_user_get_discount_code(self, brand_slug: str, username: str) -> bool:
        last_time = self._last_get_code_time.get(username, {}).get(brand_slug)
        if not last_time:
            return True

        passed_time = datetime.now() - last_time
        if passed_time >= self.min_passed_time:
            return True
        else:
            return False


simple_limiter_singleton = SimpleInMemoryLimiter(
    timedelta(seconds=settings.SIMPLE_LIMITER_RATE_LIMIT_SECONDS)
)
