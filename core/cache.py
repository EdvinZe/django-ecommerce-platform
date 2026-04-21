import logging
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

def get_or_set_cache(key, fetch_func, timeout=60 * 60 * 24, cache_empty=True):
    key = f"{settings.CACHE_NAMESPACE}:{key}"

    try:
        cached = cache.get(key)

        if cached is not None:
            logger.info(f"{key} → cache HIT")
            return cached

        logger.info(f"{key} → cache MISS")

        data = fetch_func()

        if data is None:
            logger.warning(f"{key} → fetch returned None")
            return None

        if data or cache_empty:
            cache.set(key, data, timeout=timeout)
            logger.info(f"{key} → cached")

        return data

    except Exception as e:
        logger.error(f"{key} → cache error: {e}")

        cached = cache.get(key)
        if cached is not None:
            logger.warning(f"{key} → fallback cache used")
            return cached

        return None
    


def invalidate_cache(key):
    full_key = f"{settings.CACHE_NAMESPACE}:{key}"
    cache.delete(full_key)
    logger.info(f"{full_key} → cache DELETED")