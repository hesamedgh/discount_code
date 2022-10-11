from logging import getLogger

from django.conf import settings
from datetime import datetime, timedelta


logger = getLogger(__name__)


class BrandPageService:
    # {brand_slug: {info: {notify_info here}, ttl: timetolive}}
    notify_info_cache_TTL = timedelta(
        hours=settings.NOTIFY_INFO_CACHE_TTL_HOURS
    )
    notify_info_in_memory_cache = {}
    NOTIFY_CACHE_INFO_KEY = "info"
    NOTIFY_CACHE_TTL_KEY = "ttl"

    @classmethod
    def request_notify_info(cls, brand_slug: str) -> dict:
        # This is mock client.
        # This should request the brand page service
        # And get notification method and data like webhook and url.
        try:
            return {  # This should be real request
                "method": "webhook",
                "data": {
                    "url": "api.mybrand.com/notifyaboutuser"
                }
            }
        except Exception as e:
            logger.error(str(e))
            return {}

    @classmethod
    def get_notify_info(cls, brand_slug: str) -> dict:
        # This is a wrapper to cache request_info data.
        # Brand notification data is pretty cachable.
        notify_info = cls.notify_info_in_memory_cache.get(brand_slug)
        if not notify_info or datetime.now() > notify_info.get(cls.NOTIFY_CACHE_TTL_KEY):
            info = cls.request_notify_info(brand_slug)
            if not info:
                return {}  # Dont cache empty response!
            cls.notify_info_in_memory_cache[brand_slug] = {
                cls.NOTIFY_CACHE_INFO_KEY: info,
                cls.NOTIFY_CACHE_TTL_KEY: datetime.now() + cls.notify_info_cache_TTL
            }

        return cls.notify_info_in_memory_cache[brand_slug][cls.NOTIFY_CACHE_INFO_KEY]
