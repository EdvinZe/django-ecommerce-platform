from django.test import TestCase
from orders.models import Order
from products.models import Product, Category


class OrderSelectorsTest(TestCase):

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



    def test_reserved_orders_count_user(self):
        Order.objects.create(
            user=None,
            session_key="abc",
            first_name="John",
            last_name="Doe",
            phone_number="+37060000000",
            email="test@test.com",
            delivery_method="parcel",
            payment_method="card",
            price=100,
            status="reserved"
        )

        count = Order.objects.filter(status="reserved").count()

        self.assertEqual(count, 1)

    def test_reserved_orders_count_session(self):
        Order.objects.create(
            session_key="abc",
            first_name="John",
            last_name="Doe",
            phone_number="+37060000000",
            email="test@test.com",
            delivery_method="parcel",
            payment_method="card",
            price=100,
            status="reserved"
        )

        from orders.selectors import reserved_orders_count

        count = reserved_orders_count(None, "abc")

        self.assertEqual(count, 1)


    def test_get_user_orders_filters_status(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user = User.objects.create(username="test")

        Order.objects.create(
            user=user,
            first_name="A",
            last_name="B",
            phone_number="+37060000000",
            email="a@test.com",
            delivery_method="parcel",
            payment_method="card",
            price=100,
            status="paid"
        )

        Order.objects.create(
            user=user,
            first_name="A",
            last_name="B",
            phone_number="+37060000000",
            email="a@test.com",
            delivery_method="parcel",
            payment_method="card",
            price=100,
            status="reserved"
        )

        Order.objects.create(
            user=user,
            first_name="A",
            last_name="B",
            phone_number="+37060000000",
            email="a@test.com",
            delivery_method="parcel",
            payment_method="card",
            price=100,
            status="pending"
        )

        request = type("Request", (), {"user": user})()

        from orders.selectors import get_user_orders

        orders = get_user_orders(request)

        self.assertEqual(orders.count(), 2)

    def test_get_user_orders_ordering(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user = User.objects.create(username="test")

        order1 = Order.objects.create(
            user=user,
            first_name="A",
            last_name="B",
            phone_number="+37060000000",
            email="a@test.com",
            delivery_method="parcel",
            payment_method="card",
            price=100,
            status="paid"
        )

        order2 = Order.objects.create(
            user=user,
            first_name="A",
            last_name="B",
            phone_number="+37060000000",
            email="a@test.com",
            delivery_method="parcel",
            payment_method="card",
            price=100,
            status="reserved"
        )

        request = type("Request", (), {"user": user})()

        from orders.selectors import get_user_orders

        orders = list(get_user_orders(request))

        self.assertEqual(orders[0].id, order2.id) 