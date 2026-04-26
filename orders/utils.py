from django.contrib import messages
from django.core.exceptions import ValidationError
from cart.models import Cart
from orders.models import Order, OrderItem
from products.models import Product
from users.utils import get_or_create_session_key


def order_item_create(cart_items, order):
    for item in cart_items:
        product = Product.objects.select_for_update().get(pk=item.product_id)
        quantity = item.quantity

        if not product.is_service and product.quantity < quantity:
            raise ValidationError(f"Ne užtenka produkto {product.name}, liko {product.quantity}")

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price_discount(),
            name=product.name,
        )

        if not product.is_service:
            product.quantity -= quantity
            product.save(update_fields=["quantity"])

    cart_items.delete()

    return True


def get_cart_items(request):
    delivery_product = Product.get_delivery_product()

    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user).exclude(product=delivery_product).select_related("product")

    session_key = get_or_create_session_key(request)
    return Cart.objects.filter(session_key=session_key).exclude(product=delivery_product).select_related("product")

def get_cart_items_by_order(order):
    delivery_product = Product.get_delivery_product()

    if order.user:
        return Cart.objects.filter(user=order.user).exclude(product=delivery_product).select_related("product")

    return Cart.objects.filter(session_key=order.session_key).exclude(product=delivery_product).select_related("product")

def order_validate_stock(cart_items, request):
    for item in cart_items:
        if item.product.quantity < item.quantity:
            messages.warning(
                request,
                f"Ne užtenka produkto {item.product.name}, sandelyje, liko {item.product.quantity}",
            )
            return False
    return True