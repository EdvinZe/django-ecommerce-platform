from cart.models import Cart
from orders.utils import get_cart_items
from products.models import Product
from users.utils import get_or_create_session_key
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def get_users_carts(request):
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user).select_related("product").order_by("id")
    
    if not request.session.session_key:
        request.session.create()
    
    return Cart.objects.filter(session_key=request.session.session_key).select_related("product").order_by("id")


def can_add_product_to_cart(request, product):
    cart_item = (
        get_cart_items(request)
        .filter(product=product)
        .first()
    )

    cart_qty = cart_item.quantity if cart_item else 0

    return cart_qty < product.quantity


def cart_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        carts = get_users_carts(request)
        delivery_product = Product.get_delivery_product()
        real_items = carts.exclude(product=delivery_product)

        if not real_items.exists():

            remove_delivery_from_cart(
                request.user if request.user.is_authenticated else None,
                request.session.session_key
            )

            messages.warning(request, "Krepšelis tuščias")
            return redirect("users_cart")

        return view_func(request, *args, **kwargs)

    return _wrapped_view

def ensure_delivery_in_cart(user, session_key):
    delivery_product = Product.get_delivery_product()

    if user:
        Cart.objects.get_or_create(
            user=user,
            product=delivery_product,
            defaults={"quantity": 1, "session_key": None}
        )
    else:
        Cart.objects.get_or_create(
            session_key=session_key,
            product=delivery_product,
            defaults={"quantity": 1, "user": None}
        )


def remove_delivery_from_cart(user, session_key):

    delivery_product = Product.get_delivery_product()

    if user:
        Cart.objects.filter(
            user=user,
            product=delivery_product
        ).delete()
    else:
        Cart.objects.filter(
            session_key=session_key,
            product=delivery_product
        ).delete()

def sync_delivery(cart_items, user, session_key):
    delivery_product = Product.get_delivery_product()

    has_products = cart_items.exclude(product=delivery_product).exists()

    if has_products:
        ensure_delivery_in_cart(user, session_key)
    else:
        remove_delivery_from_cart(user, session_key)