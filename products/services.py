from django.shortcuts import get_object_or_404
from core.cache import get_or_set_cache
from products.models import Category, Product
from django.shortcuts import get_object_or_404
from core.cache import get_or_set_cache
from products.models import Category, Product
import random
from django.db.models import Case, When
from django.core.cache import cache
import random
from django.db.models import Case, When

MAIN_PRODUCTS_TIMEOUT = 60 * 5


def fetch_main_products():
    return list(
    Product.objects.visible()[:3]
    )


def get_main_products():
    return get_or_set_cache(
        key="main_products",
        fetch_func=fetch_main_products,
        timeout=MAIN_PRODUCTS_TIMEOUT
    )

CATEGORY_TIMEOUT = 60 * 10

def fetch_categories():
    return list(
        Category.objects.filter(is_visible=True)
    )


def get_categories():
    return get_or_set_cache(
        key="categories",
        fetch_func=fetch_categories,
        timeout=CATEGORY_TIMEOUT
    )


CATALOG_TIMEOUT = 60 * 2


def get_catalog_version():
    version = cache.get("catalog_version")

    if version is None:
        version = 1
        cache.set("catalog_version", version)

    return version

def normalize(val):
    return str(val) if val else "none"

def build_catalog_key(category_slug, on_sale, order_by, query, page):
    version = get_catalog_version()

    return f"catalog:v{version}:{category_slug}:{normalize(on_sale)}:{normalize(order_by)}:{normalize(query)}:{page}"


def fetch_catalog_ids(category_slug, on_sale, order_by, query):
    from .utils import search_q

    products = Product.objects.visible()

    if query:
        products = search_q(query).filter(
            is_visible=True,
            category__is_visible=True
        )

    if category_slug != 'all':
        products = products.filter(category__slug=category_slug)

    if on_sale:
        products = products.filter(discount__gt=0)

    if order_by and order_by != 'default':
        products = products.order_by(order_by)

    return list(products.values_list("id", flat=True))


def get_catalog_ids(category_slug, on_sale, order_by, query, page):
    key = build_catalog_key(category_slug, on_sale, order_by, query, page)

    return get_or_set_cache(
        key=key,
        fetch_func=lambda: fetch_catalog_ids(
            category_slug, on_sale, order_by, query
        ),
        timeout=CATALOG_TIMEOUT
    )


PRODUCT_TIMEOUT = 60 * 5


def fetch_product(slug):
    return get_object_or_404(Product.objects.visible(), slug=slug)


def get_product(slug):
    return get_or_set_cache(
        key=f"product:{slug}",
        fetch_func=lambda: fetch_product(slug),
        timeout=PRODUCT_TIMEOUT
    )


def fetch_related_products(product_id):
    qs = Product.objects.visible().exclude(id=product_id)

    ids = list(qs.values_list("id", flat=True))

    if not ids:
        return []

    selected_ids = random.sample(ids, min(len(ids), 4))

    preserved_order = Case(
        *[When(id=pk, then=pos) for pos, pk in enumerate(selected_ids)]
    )

    return list(
        Product.objects.visible().filter(id__in=selected_ids)
        .order_by(preserved_order)
    )


def get_related_products(product_id):
    return get_or_set_cache(
        key=f"related:{product_id}",
        fetch_func=lambda: fetch_related_products(product_id),
        timeout=60 * 5
    )