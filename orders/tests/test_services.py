from django.test import TestCase
from cart.models import Cart
from products.models import Product, Category
from orders.models import Order
from orders.services import (
    order_create_object,
    order_update_object,
    get_existing_unpaid_order,
    update_order_status,
)

class OrderServiceTest(TestCase):

    def setUp(self):
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

        self.cart = Cart.objects.create(product=self.product, quantity=2)

        class DummyForm:
            cleaned_data = {
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "+37060000000",
                "email": "test@test.com",
                "delivery_method": "parcel",
                "payment_method": "card",
                "locker": "123",
                "locker_company": "omniva",
            }

        self.form = DummyForm()

    def test_order_create_object(self):
        order = order_create_object(
            user=None,
            session_key="abc",
            form=self.form,
            cart_items=Cart.objects.all()
        )

        self.assertEqual(order.price, 200)
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.locker, "123")

    def test_order_update_object(self):
        order = Order.objects.create(
            first_name="Old",
            last_name="User",
            phone_number="+37060000000",
            email="old@test.com",
            delivery_method="parcel",
            payment_method="card",
            price=100
        )

        updated = order_update_object(
            form=self.form,
            cart_items=Cart.objects.all(),
            order=order
        )

        self.assertEqual(updated.first_name, "John")
        self.assertEqual(updated.price, 200)
    
    def test_get_existing_unpaid_order(self):
        order = Order.objects.create(
            session_key="abc",
            first_name="John",
            last_name="Doe",
            phone_number="+37060000000",
            email="test@test.com",
            delivery_method="parcel",
            payment_method="card",
            price=100,
            status="pending"
        )

        found = get_existing_unpaid_order(None, "abc")

        self.assertEqual(found.id, order.id)
    
    def test_update_order_status(self):
        order = Order.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="+37060000000",
            email="test@test.com",
            delivery_method="parcel",
            payment_method="card",
            price=100
        )

        update_order_status(order, "paid")

        order.refresh_from_db()

        self.assertEqual(order.status, "paid")