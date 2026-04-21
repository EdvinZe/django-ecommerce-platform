from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from products.models import Product, Category
from cart.models import Cart
from orders.models import Order
from cart.utils import DELIVERY_PRODUCT_ID


class CreateOrderViewTest(TestCase):

    def setUp(self):
        self.client = Client()

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

        Product.objects.create(
            id=DELIVERY_PRODUCT_ID,
            category=self.category,
            name="Delivery",
            price=5,
            discount=0,
            short_description="delivery",
            long_description="delivery",
            quantity=100,
            image="test.jpg"
        )

        self.url = reverse("order_form")

    def create_cart(self):
        session = self.client.session
        session.save()

        return Cart.objects.create(
            session_key=session.session_key,
            product=self.product,
            quantity=1
        )

    def valid_data(self, payment="cash"):
        return {
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+37060055422",
            "email": "test@gmail.com",
            "delivery_method": "parcel",
            "payment_method": payment,
            "locker": "123",
            "locker_company": "omniva",
        }

    # @patch("orders.views.get_cart_items")
    # @patch("orders.views.email_order_reserved")
    # @patch("orders.views.remove_delivery_from_cart")
    # @patch("orders.views.ensure_delivery_in_cart")
    # @patch("orders.views.order_validate_stock")
    # def test_create_order_cash_success(
    # self, mock_validate, mock_ensure, mock_remove, mock_email, mock_get_cart
    # ):
    #     self.create_cart()

    #     mock_get_cart.return_value = Cart.objects.all()
    #     mock_validate.return_value = True

    @patch("orders.views.remove_delivery_from_cart")
    @patch("orders.views.ensure_delivery_in_cart")
    @patch("orders.views.order_validate_stock")
    def test_create_order_card_redirect(
        self, mock_validate, mock_ensure, mock_remove
    ):
        self.create_cart()
        mock_validate.return_value = True

        data = self.valid_data("card")
        data["locker"] = "12345"
        data["accept_terms"] = True 

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/payments/create_stripe_session/", response.url)

    @patch("orders.views.get_cart_items")
    def test_create_order_empty_cart(self, mock_get_cart):
        mock_get_cart.return_value = Cart.objects.none()

        response = self.client.post(self.url, self.valid_data())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 0)
