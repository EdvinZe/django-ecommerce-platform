from django.contrib import admin

from notifications.admin import EmailLogInline
from orders.models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = (
        "product",
        "quantity",
        "price",
    )

    can_delete = False

    def has_add_permission(self, request, obj):
        return False
    

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "user", 
        "email",
        "delivery_method",
        "payment_method",
        "status",
        "price",
        "shipment_requested",
        "created_at"
        )
    
    search_fields = ("id",)
    inlines = [OrderItemInline, EmailLogInline]
    list_filter = ("status",)
    
    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True

        return obj.status in ("reserved", "pending")
    

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = (
        "product",
        "quantity",
        "price",
    )

    can_delete = False

    def has_add_permission(self, request, obj):
        return False
    