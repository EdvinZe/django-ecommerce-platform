from rest_framework import serializers
from orders.models import Order, OrderItem
from lockers.models import Shipment

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("name", "quantity", "price")

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = (
            "provider",
            "tracking_number",
            "label_url",
        )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source="orderitem_set", many=True)
    shipment = ShipmentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "status",
            "delivery_method",
            "locker_company",
            "locker",
            "created_at",
            "items",
            "shipment",
        )
