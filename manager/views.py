import logging
import qrcode
from backend import settings
from lockers.services import send_to_carrier
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from manager.utils import manager_required
from notifications.models import PushSubscription
from orders.models import Order
from lockers.models import Shipment


logger = logging.getLogger(__name__)


@manager_required
def manager_order_qr_view(request, order_id):
    try:
        shipment = Shipment.objects.get(order_id=order_id)
    except Shipment.DoesNotExist:
        logger.error(f"[AUDIT] QR shipment not found Order={order_id}")
        return HttpResponse(status=404)

    logger.info(f"[AUDIT] Manager viewed QR Order={order_id}")

    img = qrcode.make(shipment.tracking_number)

    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response

@manager_required
def manager_orders_list(request):
    orders = Order.objects.select_related("user").order_by("-created_at")
    push_enabled = PushSubscription.objects.filter(user=request.user).exists()

    status = request.GET.get("status")
    delivery = request.GET.get("delivery")

    if status:
        orders = orders.filter(status=status)

    if delivery:
        orders = orders.filter(delivery_method=delivery)

    context = {
        "orders": orders,
        "current_status": status,
        "current_delivery": delivery,
        "VAPID_PUBLIC_KEY": settings.VAPID_PUBLIC_KEY,
        "push_enabled": push_enabled,
    }

    return render(request, "manager/orders_list.html", context)


@manager_required
def manager_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    shipment = Shipment.objects.filter(order=order).first()
    items = order.orderitem_set.select_related("product")

    context = {
        "order": order,
        "shipment": shipment,
        "items": items,
    }

    return render(request, "manager/order_detail.html", context)



@manager_required
@require_POST
def manager_mark_packed(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status != "registered":
        logger.warning(f"[AUDIT] Invalid pack attempt Order={order.id}")
        return redirect("manager_order_detail", order_id=order.id)

    order.status = "packed"
    order.save(update_fields=["status"])

    logger.info(f"[AUDIT] Manager={request.user.id} packed Order={order.id}")

    return redirect("manager_order_detail", order_id=order.id)


@manager_required
@require_POST
def manager_mark_shipped(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status != "packed":
        logger.warning(f"[AUDIT] Invalid shipped attempt Order={order.id}")
        return redirect("manager_order_detail", order_id=order.id)

    if not Shipment.objects.filter(order=order).exists():
        logger.warning(f"[AUDIT] Shipment missing Order={order.id}")
        return redirect("manager_order_detail", order_id=order.id)

    order.status = "shipped"
    order.save(update_fields=["status"])

    logger.info(f"[AUDIT] Manager={request.user.id} marked shipped Order={order.id}")

    return redirect("manager_order_detail", order_id=order.id)

@manager_required
@require_POST
def manager_mark_completed(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.delivery_method == "parcel" and order.status not in {"shipped", "packed"}:
        logger.warning(f"[AUDIT] Invalid complete attempt Order={order.id}")
        return redirect("manager_order_detail", order_id=order.id)

    order.status = "completed"
    order.save(update_fields=["status"])

    logger.info(f"[AUDIT] Manager={request.user.id} completed Order={order.id}")

    return redirect("manager_order_detail", order_id=order.id)


@manager_required
@require_POST
def manager_bulk_mark_packed(request):
    order_ids = request.POST.getlist("order_ids")

    if not order_ids:
        return redirect("manager_orders_list")

    try:
        order_ids = [int(oid) for oid in order_ids]
    except (ValueError, TypeError):
        logger.warning(f"[AUDIT] Manager={request.user.id} bulk pack invalid ids={order_ids}")
        return redirect("manager_orders_list")

    Order.objects.filter(
        id__in=order_ids,
        status="paid",
    ).update(status="packed")

    logger.info(f"[AUDIT] Manager={request.user.id} bulk packed Orders={order_ids}")

    return redirect("manager_orders_list")

@manager_required
@require_POST
def manager_cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status not in {"pending", "reserved"}:
        logger.warning(f"[AUDIT] Invalid cancel attempt Order={order.id}")
        return redirect("manager_order_detail", order_id=order.id)

    order.status = "cancelled"
    order.save(update_fields=["status"])

    logger.warning(f"[AUDIT] Manager={request.user.id} cancelled Order={order.id}")

    return redirect("manager_orders_list")

@manager_required
@require_POST
def manager_retry_shipment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status != "shipping_error":
        return HttpResponseNotAllowed("Cannot retry this order")
    
    logger.warning(f"[AUDIT] Manager retry shipment Order={order.id}")

    send_to_carrier(order)

    return redirect("manager_order_detail", order_id=order.id)