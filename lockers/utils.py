import requests
from lockers.serializers import OmnivaResponseSerializer
from lockers.models import Shipment
import logging
import base64
from django.conf import settings
from .api_configs import DPDConfig


logger = logging.getLogger(__name__)

def parse_provider_response(provider, response_json):
    if provider == "omniva":
        serializer = OmnivaResponseSerializer(data=response_json)
        serializer.is_valid(raise_exception=True)

        shipments = serializer.validated_data["savedShipments"]

        if not shipments:
            raise ValueError("No shipments created by Omniva")

        shipment = shipments[0]

        return {
            "partner_shipment_id": shipment["clientItemId"],
            "barcode": shipment["barcode"],
        }

    elif provider == "dpd":
        return {
            "partner_shipment_id": response_json["shipmentId"],
            "barcode": response_json.get("parcelNumber"),
        }

    elif provider == "lp_express":
        return {
            "partner_shipment_id": response_json["order_id"],
            "barcode": response_json.get("barcode"),
        }

    else:
        raise ValueError(f"Unknown provider {provider}")
    
def build_barcode_url(provider, barcode):
    return f"{settings.SITE_URL}/lockers/shipment/{provider}/{barcode}/"


def get_dpd_token():
    url = f"{DPDConfig.BASE_URL}/auth/me"

    logger.info(f"DPD → requesting token | url={url}")

    credentials = f"{DPDConfig.USERNAME}:{DPDConfig.PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded}",
        "Accept": "application/json",
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json={"name": "my-token"},
            timeout=5,
        )
    except requests.RequestException as e:
        logger.error(f"DPD → request failed: {e}")
        return None

    logger.debug(f"DPD → request headers: {response.request.headers}")

    logger.info(f"DPD → status={response.status_code}")
    logger.info(f"DPD → content-type={response.headers.get('Content-Type')}")

    try:
        data = response.json()
        logger.info(f"DPD → response JSON: {data}")
    except Exception:
        logger.warning(f"DPD → non-JSON response: {response.text}")
        return None

    if response.status_code != 200:
        logger.error(f"DPD → auth failed | status={response.status_code} | response={data}")
        return None

    token = data.get("token")

    if not token:
        logger.error(f"DPD → token missing in response: {data}")
        return None

    logger.info("DPD → token successfully received")

    return token
