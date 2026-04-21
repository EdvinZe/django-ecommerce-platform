from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from cart.models import Cart
from products.models import Product, Category
from orders.models import Order, OrderItem
from orders.utils import (
    order_item_create,
    order_validate_stock,
)

class OrderUtilsTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.category = Category.objects.create(name="Test")

        self.product = Product.objects.create(
            category=self.category,
            name="Product",
            price=100,
            discount=0,
            short_description="short",
            long_description="long",
            quantity=10,
            image="test.jpg"
        )

        self.order = Order.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="+37060000000",
            email="test@test.com",
            delivery_method="parcel",
            payment_method="card",
            price=100
        )


    def test_order_item_create_creates_items(self):
        Cart.objects.create(product=self.product, quantity=2)

        order_item_create(Cart.objects.all(), self.order)

        self.assertEqual(OrderItem.objects.count(), 1)

    def test_order_item_create_reduces_stock(self):
        Cart.objects.create(product=self.product, quantity=2)

        order_item_create(Cart.objects.all(), self.order)

        self.product.refresh_from_db()

        self.assertEqual(self.product.quantity, 8)

    def test_order_item_create_clears_cart(self):
        Cart.objects.create(product=self.product, quantity=2)

        order_item_create(Cart.objects.all(), self.order)

        self.assertEqual(Cart.objects.count(), 0)

    def test_order_item_create_does_not_reduce_service(self):
        self.product.is_service = True
        self.product.save()

        Cart.objects.create(product=self.product, quantity=2)

        order_item_create(Cart.objects.all(), self.order)

        self.product.refresh_from_db()

        self.assertEqual(self.product.quantity, 10)



    def test_order_validate_stock_ok(self):
        request = self.factory.get("/")

        Cart.objects.create(product=self.product, quantity=2)

        result = order_validate_stock(Cart.objects.all(), request)

        self.assertTrue(result)

    def test_order_validate_stock_fail(self):
        request = self.factory.get("/")

        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        self.product.quantity = 1
        self.product.save()

        Cart.objects.create(product=self.product, quantity=5)

        result = order_validate_stock(Cart.objects.all(), request)

        self.assertFalse(result)