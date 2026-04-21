from django.db import models
from backend import settings
from orders.models import Order

class EmailLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    email_type = models.CharField(max_length=64)
    to = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)


class PushSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    endpoint = models.TextField(unique=True)
    p256dh = models.TextField()
    auth = models.TextField()
