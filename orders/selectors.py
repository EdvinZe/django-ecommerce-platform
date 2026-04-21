from orders.models import Order


def reserved_orders_count(user, session_key):
    if user:
        return Order.objects.filter(user=user, status="reserved").count()
    return Order.objects.filter(session_key=session_key, status="reserved").count()


def get_user_orders(request):
    return (
        Order.objects
        .filter(
            user=request.user,
            status__in=["reserved", "delivered", "paid", "registered", "cancelled", "packed"]
        )
        .order_by("-created_at")
    )
