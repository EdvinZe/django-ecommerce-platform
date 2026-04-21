from django.test import TestCase
from unittest.mock import patch, Mock
import requests

from lockers.utils import parse_provider_response, get_dpd_token


class ParseProviderResponseTest(TestCase):

    @patch("lockers.utils.OmnivaResponseSerializer")
    def test_omniva_success(self, mock_serializer):
        mock_instance = Mock()
        mock_instance.is_valid.return_value = True
        mock_instance.validated_data = {
            "savedShipments": [
                {
                    "clientItemId": "123",
                    "barcode": "ABC123"
                }
            ]
        }

        mock_serializer.return_value = mock_instance

        result = parse_provider_response("omniva", {})

        self.assertEqual(result["partner_shipment_id"], "123")
        self.assertEqual(result["barcode"], "ABC123")

    @patch("lockers.utils.OmnivaResponseSerializer")
    def test_omniva_empty(self, mock_serializer):
        mock_instance = Mock()
        mock_instance.is_valid.return_value = True
        mock_instance.validated_data = {
            "savedShipments": []
        }

        mock_serializer.return_value = mock_instance

        with self.assertRaises(Exception):
            parse_provider_response("omniva", {})

    def test_dpd_success(self):
        data = {
            "shipmentId": "DPD123",
            "parcelNumber": "TRACK123"
        }

        result = parse_provider_response("dpd", data)

        self.assertEqual(result["partner_shipment_id"], "DPD123")
        self.assertEqual(result["barcode"], "TRACK123")

    def test_lp_success(self):
        data = {
            "order_id": "LP123",
            "barcode": "BAR123"
        }

        result = parse_provider_response("lp_express", data)

        self.assertEqual(result["partner_shipment_id"], "LP123")
        self.assertEqual(result["barcode"], "BAR123")

    def test_unknown_provider(self):
        with self.assertRaises(ValueError):
            parse_provider_response("invalid", {})


class GetDPDTokenTest(TestCase):

    @patch("lockers.utils.requests.post")
    def test_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "abc123"}

        mock_post.return_value = mock_response

        token = get_dpd_token()

        self.assertEqual(token, "abc123")

    @patch("lockers.utils.requests.post")
    def test_no_token(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        mock_post.return_value = mock_response

        token = get_dpd_token()

        self.assertIsNone(token)

    @patch("lockers.utils.requests.post")
    def test_http_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}

        mock_post.return_value = mock_response

        token = get_dpd_token()

        self.assertIsNone(token)

    @patch("lockers.utils.requests.post")
    def test_exception(self, mock_post):
        mock_post.side_effect = requests.RequestException("fail")

        token = get_dpd_token()

        self.assertIsNone(token)