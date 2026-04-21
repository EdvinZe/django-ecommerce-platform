from django.forms import ValidationError
from backend import settings
from orders.models import Order


def order_create_object(user, session_key, form, cart_items):
    locker_company = ""
    locker = ""

    if form.cleaned_data["delivery_method"] == "parcel":
        locker = form.cleaned_data["locker"]
        locker_company = form.cleaned_data["locker_company"]

    return Order.objects.create(
        user=user,
        session_key=session_key,
        first_name=form.cleaned_data["first_name"],
        last_name=form.cleaned_data["last_name"],
        phone_number=form.cleaned_data["phone_number"],
        email=form.cleaned_data["email"],
        delivery_method=form.cleaned_data["delivery_method"],
        payment_method=form.cleaned_data["payment_method"],
        locker_company=locker_company,
        locker=locker,
        price=cart_items.total_price(),
        status="pending",
    )


def order_update_object(form, cart_items, order):
    locker_company = ""
    locker = ""

    if form.cleaned_data["delivery_method"] == "parcel":
        locker = form.cleaned_data["locker"]
        locker_company = form.cleaned_data["locker_company"]

    order.first_name = form.cleaned_data["first_name"]
    order.last_name = form.cleaned_data["last_name"]
    order.phone_number = form.cleaned_data["phone_number"]
    order.email = form.cleaned_data["email"]
    order.delivery_method = form.cleaned_data["delivery_method"]
    order.payment_method = form.cleaned_data["payment_method"]
    order.locker_company = locker_company
    order.locker = locker
    order.price = cart_items.total_price()
    order.status = "pending"
    order.save()

    return order


def get_existing_unpaid_order(user, session_key):
    if user:
        return Order.objects.filter(user=user, status__in=["pending", "failed"]).first()

    return Order.objects.filter(
        session_key=session_key, status__in=["pending", "failed"]
    ).first()


def update_order_status(order, new_status):
    order.status = new_status
    order.save(update_fields=["status"])
    return order


def validate_payment_type(payment_type):
    if payment_type == "on_pickup" and not settings.ENABLE_PICKUP:
        raise ValidationError("Pickup is temporarily unavailable")
