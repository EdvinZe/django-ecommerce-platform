from django.contrib import messages
from cart.models import Cart
from orders.models import Order, OrderItem
from users.utils import get_or_create_session_key


def order_item_create(cart_items, order):
    for item in cart_items:
        product = item.product
        name = item.product.name
        price = item.product.price_discount()
        quantity = item.quantity

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=price,
            name=name,
        )

        if not product.is_service:
            product.quantity -= quantity

        product.save()

    cart_items.delete()

    return True


def get_cart_items(request):
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user)

    session_key = get_or_create_session_key(request)

    return Cart.objects.filter(session_key=session_key)


def get_cart_items_by_order(order):
    if order.user:
        return Cart.objects.filter(user=order.user)

    return Cart.objects.filter(session_key=order.session_key)


def order_validate_stock(cart_items, request):
    for item in cart_items:
        if item.product.quantity < item.quantity:
            messages.warning(
                request,
                f"Ne užtenka produkto {item.product.name}, sandelyje, liko {item.product.quantity}",
            )
            return False
    return True