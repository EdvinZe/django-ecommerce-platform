from django.contrib import admin

from products.models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ("name", "is_visible")
    list_display = ("name", "is_visible")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fields=(
    "category",
    "name",
    "price",
    "discount",
    "short_description",
    "long_description",
    "quantity",
    "image",
    "unit",
    "is_visible",
    "is_service",
    )

    list_display = (
        "category",
        "name",
        "price",
        "unit",
        "discount",
        "quantity",
        "is_visible",

    )

    search_fields = ("name",)
    list_filter = ("name", "category")
