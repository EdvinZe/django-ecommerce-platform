from django.contrib import admin

from lockers.models import Shipment

from django.contrib import admin


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "provider",
        "label_url",
        "shipment_id",
        "tracking_number",
        "created_at",
    )

    list_filter = ("provider",)
    ordering = ("-created_at",)

    readonly_fields = (
        "order",
        "provider",
        "label_url",
        "shipment_id",
        "tracking_number",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
