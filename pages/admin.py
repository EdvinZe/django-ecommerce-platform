from .models import GalleryImage
from django.contrib import admin

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_visible', 'order')
    list_editable = ('is_visible', 'order')