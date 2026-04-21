from django.contrib import admin
from notifications.models import EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "email_type",
        "to",
        "sent_at",
    )

    list_filter = ("email_type",)
    readonly_fields = ("order", "email_type", "to", "sent_at")
    ordering = ("-sent_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class EmailLogInline(admin.TabularInline):
    model = EmailLog
    extra = 0
    readonly_fields = ("email_type", "to", "sent_at")
    can_delete = False

    def has_add_permission(self, request, obj):
        return False
