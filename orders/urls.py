from django.urls import path
from orders.views import create_order

urlpatterns = [
    path("order_form/", create_order, name="order_form"),
]
