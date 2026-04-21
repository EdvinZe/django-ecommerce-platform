from .models import SiteSettings
from core.cache import get_or_set_cache  


def site_settings(request):
    return {
        "site_settings": get_or_set_cache(
            key="site_settings",
            fetch_func=SiteSettings.load,
            timeout=None,
        )
    }