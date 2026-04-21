from re import I
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from orders.models import Order
from .serializers import OrderSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from notifications.models import PushSubscription


class ManagerOrdersView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return (
            Order.objects.select_related("shipment")
            .prefetch_related("orderitem_set")
            .order_by("-created_at")
        )


class ManagerMarkPacked(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        if order.status != "paid":
            return Response({"error": "Invalid status"}, status=400)

        order.status = "packed"
        order.save(update_fields=["status"])

        return Response({"status": "packed"})


class SaveSubscription(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        if not request.user.is_staff:
            return Response({"error": "Forbidden"}, status=403)

        data = request.data

        PushSubscription.objects.update_or_create(
            endpoint=data["endpoint"],
            defaults={
                "user": request.user,
                "p256dh": data["keys"]["p256dh"],
                "auth": data["keys"]["auth"],
            },
        )

        return Response({"status": "ok"})
    

class PushSubscriptionStatus(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        exists = PushSubscription.objects.filter(user=request.user).exists()
        return Response({"subscribed": exists})
    
class DeleteSubscription(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        PushSubscription.objects.filter(user=request.user).delete()
        return Response({"status": "deleted"})