from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):

    fieldsets = (
        ("Company", {
            "fields": (
                "company_name",
                "brand_name",
                "email",
                "phone",
            )
        }),

        ("Address", {
            "fields": (
                "address",
                "city",
                "postal_code",
                "country",
            )
        }),

        ("Support", {
            "fields": (
                "support_email",
                "support_phone",
                "working_hours",
            )
        }),

        ("Social", {
            "fields": (
                "facebook_url",
                "instagram_url",
                "telegram_url",
                "youtube_url",
                "tiktok_url",
            )
        }),

        ("Legal", {
            "fields": (
                "company_code",
                "vat_code",
                "privacy_email",
                "terms_last_updated",
                "privacy_last_updated",
            )
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()