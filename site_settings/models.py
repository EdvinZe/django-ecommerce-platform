from django.db import models
from core.cache import invalidate_cache
from users.utils import validate_real_email
from phonenumber_field.modelfields import PhoneNumberField


class SiteSettings(models.Model):
    company_name = models.CharField(max_length=255, verbose_name="Company name")
    brand_name = models.CharField(max_length=255, blank=True, verbose_name="Brand name")

    phone = PhoneNumberField(blank=False, null=False, unique=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)

    support_phone = models.CharField(max_length=50, blank=True)
    working_hours = models.CharField(max_length=255, blank=True)

    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    telegram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    company_code = models.CharField(max_length=100, blank=True)
    vat_code = models.CharField(max_length=100, blank=True)

    terms_last_updated = models.DateField(null=True, blank=True)
    privacy_last_updated = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    email = models.EmailField(
        verbose_name="Company email",
        validators=[validate_real_email]
    )

    support_email = models.EmailField(
        blank=True,
        validators=[validate_real_email]
    )

    privacy_email = models.EmailField(
        blank=True,
        validators=[validate_real_email]
    )

    def phone_number_e164(self):
        return self.phone.as_e164

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return self.company_name or "Site settings"

    def save(self, *args, **kwargs):
        self.full_clean() 
        self.pk = 1
        super().save(*args, **kwargs)
        invalidate_cache("site_settings")

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
    
