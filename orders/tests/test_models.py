from django.test import TestCase
from django.core.cache import cache
from products.models import Product, Category
from orders.models import Order, OrderItem


class OrderModelTest(TestCase):

    def setUp(self):

        cache.clear()

        self.category = Category.objects.create(name="Test")

        self.product = Product.objects.create(
            category=self.category,
            name="Product",
            price=100,
            discount=0,
            short_description="short",
            long_description="long",
            quantity=10,
            image="test.jpg",
        )

        self.order = Order.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="+37060000000",
            email="test@test.com",
            delivery_method="parcel",
            payment_method="card",
            price=100,
        )

    def test_order_item_products_price(self):
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=100,
            name=self.product.name,
        )

        self.assertEqual(item.products_price(), 200)

    def test_order_item_products_price_with_discount(self):
        self.product.discount = 10
        self.product.save()

        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=100,
            name=self.product.name,
        )

        self.assertEqual(item.products_price(), 180)

    def test_get_fullname(self):
        self.assertEqual(self.order.get_fullname(), "John Doe")

    def test_phone_number_format(self):
        formatted = self.order.phone_number_e164()
        self.assertTrue(formatted.startswith("+"))

    def test_products_price_zero_quantity(self):
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=0,
            price=100,
            name=self.product.name,
        )

        self.assertEqual(item.products_price(), 0)

    def test_products_price_rounding(self):
        self.product.price = 99.99
        self.product.discount = 33
        self.product.save()

        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=99.99,
            name=self.product.name,
        )

        result = item.products_price()

        self.assertEqual(result, round(99.99 - 99.99 * 33 / 100, 2))
