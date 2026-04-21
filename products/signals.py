from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.cache import invalidate_cache
from .models import Product, Category
from django.core.cache import cache

def bump_catalog_version():
    try:
        cache.incr("catalog_version")
    except ValueError:
        cache.set("catalog_version", 2)

@receiver(post_save, sender=Product)
def product_saved(sender, instance, **kwargs):
    invalidate_cache("main_products")
    bump_catalog_version()

@receiver(post_delete, sender=Product)
def product_deleted(sender, instance, **kwargs):
    invalidate_cache("main_products")
    bump_catalog_version()

@receiver(post_save, sender=Category)
def category_saved(sender, instance, **kwargs):
    invalidate_cache("categories")
    bump_catalog_version()

@receiver(post_delete, sender=Category)
def category_deleted(sender, instance, **kwargs):
    invalidate_cache("categories")
    bump_catalog_version()


