from django.test import TestCase
from unittest.mock import patch, Mock
from lockers.mappers import omniva_lockers, dpd_lockers, lp_express_lockers


class LockersAPITest(TestCase):

    @patch("lockers.mappers.requests.get")
    def test_omniva_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "TYPE": "0",
                "A0_NAME": "LT",
                "ZIP": "123",
                "Y_COORDINATE": "54.1",
                "X_COORDINATE": "25.2",
                "NAME": "Test locker"
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = omniva_lockers("LT")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["provider"], "omniva")

    @patch("lockers.mappers.requests.get")
    def test_omniva_filters_wrong_country(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {"TYPE": "0", "A0_NAME": "LV"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = omniva_lockers("LT")

        self.assertEqual(len(result), 0)

    @patch("lockers.mappers.requests.get")
    def test_omniva_error(self, mock_get):
        mock_get.side_effect = Exception("fail")

        result = omniva_lockers("LT")

        self.assertEqual(result, [])

    @patch("lockers.mappers.requests.get")
    @patch("lockers.utils.get_dpd_token")
    def test_dpd_success(self, mock_token, mock_get):
        mock_token.return_value = "token"

        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "1",
                    "name": "DPD Locker",
                    "address": {
                        "latLong": "54.1,25.2"
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = dpd_lockers("LT")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["provider"], "dpd")

    @patch("lockers.mappers.requests.get")
    @patch("lockers.utils.get_dpd_token")
    def test_dpd_error(self, mock_token, mock_get):
        mock_token.return_value = "token"
        mock_get.side_effect = Exception("fail")

        result = dpd_lockers("LT")

        self.assertEqual(result, [])

    @patch("lockers.mappers.requests.get")
    def test_lp_express_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "terminalId": "1",
                "latitude": "54.1",
                "longitude": "25.2",
                "name": "LP Locker",
                "active": True
            }
        ]
        mock_get.return_value = mock_response

        result = lp_express_lockers("LT")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["provider"], "lp_express")

    @patch("lockers.mappers.requests.get")
    def test_lp_express_inactive(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {"active": False}
        ]
        mock_get.return_value = mock_response

        result = lp_express_lockers("LT")

        self.assertEqual(len(result), 0)