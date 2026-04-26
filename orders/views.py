import logging
from django.urls import reverse
from backend import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.db import transaction
from cart.utils import cart_required, ensure_delivery_in_cart, remove_delivery_from_cart
from orders.forms import OrderForm
from orders.utils import (
    get_cart_items,
    order_item_create,
    order_validate_stock,
)
from orders.selectors import reserved_orders_count
from orders.services import (
    order_create_object,
    get_existing_unpaid_order,
    order_update_object,
)
from users.utils import get_or_create_session_key
from orders.demo import demo_add_delivery_to_order, handle_demo_payment

logger = logging.getLogger(__name__)

@cart_required
def create_order(request):

    if request.user.is_authenticated:
        user = request.user
    else:
        user = None

    if request.method == "POST":
        form = OrderForm(data=request.POST)
        session_key = get_or_create_session_key(request)

        if form.is_valid():

            reserved_count = reserved_orders_count(user=user, session_key=session_key)

            if form.cleaned_data["payment_method"] == "cash" and not settings.ENABLE_PICKUP:
                messages.warning(
                    request,
                    """Norėdami rezervuoti prekę ir atsiskaityti vietoje grynais,
                    susisiekite su vadybininku. Telefono numerį rasite kontaktų skiltyje viršutiniame meniu.""",
                )
                return redirect("order_form")

            if not request.user.is_authenticated and form.cleaned_data["payment_method"] == "cash":
                messages.warning(
                    request,
                    "Norėdami rezervuoti prekes, turite prisijungti.",
                )
                return redirect("login")

            if reserved_count >= 3 and form.cleaned_data["payment_method"] == "cash":
                messages.warning(
                    request,
                    "Pasiekėte 3 rezervuotų užsakymų limitą. Negalite sukurti daugiau.",
                )
                return redirect("order_form")

            cart_items = get_cart_items(request)
            if cart_items.exists():

                if not order_validate_stock(request=request, cart_items=cart_items):
                    return redirect("order_form")

                if (
                    form.cleaned_data["delivery_method"] == "parcel"
                    and not form.cleaned_data["locker"]
                ):
                    messages.warning(request, "Pastomatas nepasirinktas")
                    return redirect("order_form")
                
                order = get_existing_unpaid_order(user=user, session_key=session_key)

                try:
                    if order:
                        with transaction.atomic():
                            order_update_object(
                                form=form, order=order, cart_items=cart_items
                            )

                            if order.payment_method == "cash":
                                order_item_create(cart_items=cart_items, order=order)
                                order.status = "reserved"
                                order.save()

                    elif not order:
                        with transaction.atomic():
                            order = order_create_object(
                                user=user,
                                session_key=session_key,
                                form=form,
                                cart_items=cart_items,
                            )

                            if order.payment_method == "cash":
                                order_item_create(cart_items=cart_items, order=order)
                                order.status = "reserved"
                                order.save()

                except ValidationError as e:
                    messages.warning(request, str(e.message))
                    return redirect("order_form")

                if order.payment_method == "card" and order.delivery_method == "parcel":
                    ensure_delivery_in_cart(user, session_key)

                elif order.delivery_method != "parcel":
                    remove_delivery_from_cart(user, session_key)

                if order.payment_method == "cash":
                    messages.success(request, "Užsakymas priimtas")
                    return redirect("main")
                


                elif order.payment_method == "card":

                    if settings.DEMO_MODE:
                        
                        if order.delivery_method == "parcel":
                            demo_add_delivery_to_order(order)

                        handle_demo_payment(order, cart_items)

                        return redirect(
                            reverse("payment_success") + f"?order={order.id}"
                        )
                    
                    return redirect("stripe_payment", order.id)

            else:
                messages.warning(request, "Krepselis tuscias")
                return redirect("order_form")

        else:
            messages.warning(request, "Klaida formoje")

    else:
        form = OrderForm()

    context = {
        "title": "Order-form",
        "form": form,
        "enable_pickup": settings.ENABLE_PICKUP,
    }

    return render(request, "orders/order.html", context)