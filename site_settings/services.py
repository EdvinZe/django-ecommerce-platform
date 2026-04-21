from .models import SiteSettings
from core.cache import get_or_set_cache


def get_site_settings():
    return get_or_set_cache(
        "site_settings",
        SiteSettings.load,
        timeout=None,
    )