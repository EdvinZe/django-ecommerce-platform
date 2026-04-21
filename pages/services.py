from django.conf import settings
from core.cache import get_or_set_cache

YEAR = 60 * 60 * 24 * 365


def fetch_gallery():
    from .models import GalleryImage
    return list(
        GalleryImage.objects
        .filter(is_visible=True)
        .order_by("order", "-created_at")
    )


def get_gallery():
    return get_or_set_cache(
        key="gallery_images",
        fetch_func=fetch_gallery,
        timeout=YEAR
    )