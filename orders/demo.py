import logging
from cart.models import Cart
from orders.models import OrderItem
from orders.utils import order_item_create
from lockers.services import send_to_carrier
from lockers.demo import demo_send_to_carrier
from products.models import Product

logger = logging.getLogger(__name__)

def handle_demo_payment(order, cart_items):

    order_item_create(cart_items=cart_items, order=order)

    order.status = "paid"
    order.save()

    logger.info(f"[DEMO] Order marked as paid Order={order.id}")

    if order.delivery_method == "parcel":
        logger.info(f"[DEMO] Shipment required Order={order.id}")
        demo_send_to_carrier(order)

    return order

def demo_add_delivery_to_order(order):
    delivery_product = Product.get_delivery_product()

    exists = order.orderitem_set.filter(product=delivery_product).exists()

    if not exists:
        OrderItem.objects.create(
            order=order,
            product=delivery_product,
            quantity=1,
            price=delivery_product.price_discount(),
            name=delivery_product.name
        )