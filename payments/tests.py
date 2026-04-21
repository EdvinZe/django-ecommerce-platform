from django.test import TestCase, Client
from unittest.mock import patch
from orders.models import Order
from products.models import Product, Category
from cart.models import Cart
import json


class StripeWebhookTest(TestCase):

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

        self.order = Order.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="+37060055422",
            email="test@gmail.com",
            delivery_method="parcel",
            payment_method="card",
            price=100,
            status="pending"
        )

        Cart.objects.create(
            product=self.product,
            quantity=1,
            session_key="test"
        )

        self.url = "/payments/stripe/webhook/"

    def fake_event(self, event_type):
        return {
            "type": event_type,
            "data": {
                "object": {
                    "client_reference_id": str(self.order.id)
                }
            }
        }

    @patch("payments.views.send_to_carrier")
    @patch("payments.views.order_item_create")
    @patch("payments.views.get_cart_items_by_order")
    @patch("payments.views.update_order_status")
    @patch("stripe.Webhook.construct_event")
    def test_payment_success(
        self,
        mock_construct,
        mock_update,
        mock_get_cart,
        mock_create_items,
        mock_carrier
    ):
        mock_construct.return_value = self.fake_event("checkout.session.completed")
        mock_get_cart.return_value = Cart.objects.all()

        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test"
        )

        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()
        mock_update.assert_called_once_with(self.order, "paid")
        mock_create_items.assert_called_once()

    @patch("payments.views.update_order_status")
    @patch("stripe.Webhook.construct_event")
    def test_payment_expired(self, mock_construct, mock_update):
        mock_construct.return_value = self.fake_event("checkout.session.expired")

        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test"
        )

        self.assertEqual(response.status_code, 200)

        mock_update.assert_called_once_with(self.order, "failed")

    @patch("stripe.Webhook.construct_event")
    def test_invalid_payload(self, mock_construct):
        mock_construct.side_effect = ValueError()

        response = self.client.post(
            self.url,
            data="invalid",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test"
        )

        self.assertEqual(response.status_code, 400)

    @patch("stripe.Webhook.construct_event")
    def test_duplicate_payment(self, mock_construct):
        self.order.status = "paid"
        self.order.save()

        mock_construct.return_value = self.fake_event("checkout.session.completed")

        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test"
        )

        self.assertEqual(response.status_code, 200)