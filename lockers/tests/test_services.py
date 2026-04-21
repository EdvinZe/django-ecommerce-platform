from django.test import TestCase
from unittest.mock import patch, Mock
from orders.models import Order
from lockers.models import Shipment


class SendToCarrierTest(TestCase):

    def setUp(self):
        self.order = Order.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="+37060055422",
            email="test@gmail.com",
            delivery_method="parcel",
            payment_method="card",
            locker="123",
            locker_company="omniva",
            price=100,
            status="paid"
        )

    @patch("lockers.services.create_shipment")
    @patch("lockers.services.send_to_omniva")
    def test_success_registered(self, mock_send, mock_create):
        from lockers.services import send_to_carrier

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "barcode": "ABC123",
            "partner_shipment_id": "SHIP123"
        }

        mock_send.return_value = mock_response
        
        mock_shipment = Mock()
        mock_create.return_value = mock_shipment

        send_to_carrier(self.order)

        self.order.refresh_from_db()

        self.assertEqual(self.order.status, "registered")
        self.assertEqual(Shipment.objects.count(), 0)

    @patch("lockers.services.send_to_omniva")
    def test_api_error(self, mock_send):
        from lockers.services import send_to_carrier

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "error"

        mock_send.return_value = mock_response

        send_to_carrier(self.order)

        self.order.refresh_from_db()

        self.assertEqual(self.order.status, "shipping_error")
        self.assertEqual(Shipment.objects.count(), 0)

    @patch("lockers.services.send_to_omniva")
    def test_exception(self, mock_send):
        from lockers.services import send_to_carrier

        mock_send.side_effect = Exception("fail")

        send_to_carrier(self.order)

        self.order.refresh_from_db()

        self.assertEqual(self.order.status, "shipping_error")

    def test_skip_if_already_registered(self):
        from lockers.services import send_to_carrier

        self.order.status = "registered"
        self.order.save()

        send_to_carrier(self.order)

        self.order.refresh_from_db()

        self.assertEqual(self.order.status, "registered")

    def test_unknown_provider(self):
        from lockers.services import send_to_carrier

        self.order.locker_company = "invalid"
        self.order.save()

        send_to_carrier(self.order)

        self.order.refresh_from_db()

        self.assertEqual(self.order.status, "shipping_error")

    @patch("lockers.services.create_shipment")
    @patch("lockers.services.send_to_omniva")
    def test_shipment_parse_fail(self, mock_send, mock_create):
        from lockers.services import send_to_carrier

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        mock_send.return_value = mock_response
        mock_create.side_effect = Exception("parse error")

        send_to_carrier(self.order)

        self.order.refresh_from_db()

        self.assertEqual(self.order.status, "shipping_error")
        self.assertEqual(Shipment.objects.count(), 0)