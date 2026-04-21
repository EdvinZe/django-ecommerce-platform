from django.db import models
from orders.models import Order


class Shipment(models.Model):
    order = models.OneToOneField(to=Order, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20)
    shipment_id = models.CharField(max_length=200)
    tracking_number = models.CharField(max_length=100, default="No number")
    label_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Shipment"
        verbose_name_plural = "Shipment"
        db_table = "Shipment"