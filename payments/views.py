from django.db import transaction
from django.shortcuts import render
import stripe
from django.conf import settings
from backend.settings import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET_KEY
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from lockers.services import send_to_carrier
from notifications.services.customer import email_order_paid, email_payment_failed
from notifications.services.push_notifications import send_push
from orders.models import Order
from orders.services import update_order_status
from orders.utils import order_item_create, get_cart_items_by_order
import logging

from products.models import Product


logger = logging.getLogger(__name__)


def stripe_payment(request, order_id):
    order = Order.objects.get(id=order_id)
    stripe.api_key = STRIPE_SECRET_KEY

    cart_items = get_cart_items_by_order(order)

    line_items = []

    for item in cart_items:
        line_items.append(
            {
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": item.product.name,
                    },
                    "unit_amount": int(item.product.price_discount() * 100),
                },
                "quantity": item.quantity,
            }
        )

    if order.delivery_method == "parcel":
        delivery_product = Product.get_delivery_product()
        line_items.append({
            "price_data": {
                "currency": "eur",
                "product_data": {"name": delivery_product.name},
                "unit_amount": int(delivery_product.price_discount() * 100),
            },
            "quantity": 1,
        })

    logger.info(f"[AUDIT] Start payment Order={order.id} user={request.user.id if request.user.is_authenticated else 'anon'}")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        client_reference_id=order.id,
        metadata={
            "order_id": order.id,
            "user": request.user if request.user.is_authenticated else False,
            "session_key": request.session.session_key,
        },
        mode="payment",
        success_url=request.build_absolute_uri(f"/payments/success/?order={order.id}"),
        cancel_url=request.build_absolute_uri(f"/payments/cancel/?order={order.id}"),
    )

    logger.info(f"[AUDIT] Stripe session created Order={order.id} session_id={session.id}")
    return redirect(session.url, code=303)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = STRIPE_WEBHOOK_SECRET_KEY

    logger.info("[AUDIT] Stripe webhook received")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

    except ValueError:
        logger.error("[AUDIT] Stripe webhook invalid payload")
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError:
        logger.error("[AUDIT] Stripe webhook signature failed")
        return HttpResponse(status=400)


    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = int(session["client_reference_id"])

        logger.info(f"[AUDIT] Payment success webhook received Order={order_id}")

        with transaction.atomic():
            try:
                order = Order.objects.select_for_update().get(id=order_id)
            except Order.DoesNotExist:
                logger.error(f"[AUDIT] Order not found Order={order_id}")
                return HttpResponse(status=404)

            if order.status == "paid":
                logger.warning(f"[AUDIT] Duplicate payment webhook Order={order.id}")
                return HttpResponse(status=200)

            update_order_status(order, "paid")
            logger.info(f"[AUDIT] Order={order.id} marked as PAID")

            cart_items = get_cart_items_by_order(order)
            order_item_create(cart_items, order)
            logger.info(f"[AUDIT] Order items created Order={order.id}")

            need_shipment = (
                order.delivery_method == "parcel"
                and not order.shipment_requested
            )

            if need_shipment:
                order.shipment_requested = True
                order.save(update_fields=["shipment_requested"])
                logger.info(f"[AUDIT] Shipment required Order={order.id}")

        email_order_paid(order)
        logger.info(f"[AUDIT] Order paid email sent Order={order.id}")

        if need_shipment:
            try:
                logger.info(f"[AUDIT] Sending Order={order.id} to carrier")
                send_to_carrier(order)
            except Exception as e:
                logger.exception(f"Carrier error for order {order.id}: {e}")

        if order.delivery_method != "parcel":
            logger.info(f"[AUDIT] Reservation email sent Order={order.id}")

        send_push()
        logger.info(f"[AUDIT] Push notification sent for Order={order.id}")


    elif event["type"] == "checkout.session.expired":
        session = event["data"]["object"]
        order_id = int(session["client_reference_id"])

        logger.warning(f"[AUDIT] Payment expired webhook Order={order_id}")

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            logger.warning(f"[AUDIT] Order not found Order={order_id}")
            return HttpResponse(status=200)

        if order.status == "paid":
            logger.warning(f"[AUDIT] Expired webhook ignored, already paid Order={order.id}")
            return HttpResponse(status=200)

        update_order_status(order, "failed")
        logger.info(f"[AUDIT] Order={order.id} marked as FAILED")

        email_payment_failed(order)
        logger.info(f"[AUDIT] Order failed email sent Order={order.id}")

    return HttpResponse(status=200)



def payment_success(request):
    order_id = request.GET.get("order")

    if not order_id:
        return redirect("main")

    order = Order.objects.filter(
        id=order_id,
        status__in=["paid", "registered"]
    ).first()

    if not order:
        return redirect("main")

    context = {
        "title": "Mokėjimas atliktas sėkmingai",
        "status": f"Užsakymas #{order.id} sėkmingai apmokėtas",
    }

    return render(request, "payments/payment_status.html", context)


def payment_cancel(request):
    order_id = request.GET.get("order")

    if not order_id:
        return redirect("main")

    order = Order.objects.filter(id=order_id).first()

    if not order or order.status not in ["paid", "registered"]:
        return redirect("payment_cancel")

    context = {
        "title": "Mokėjimas atšauktas",
        "status": f"Užsakymas #{order.id} nebuvo apmokėtas",
    }

    return render(request, "payments/payment_status.html", context)

# stripe listen --forward-to localhost:8000/payments/stripe/webhook/