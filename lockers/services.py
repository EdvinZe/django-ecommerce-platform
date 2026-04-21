import logging
from lockers.mappers import get_omniva_lockers
from lockers.models import Shipment
from lockers.utils import build_barcode_url, parse_provider_response
from lockers.dpd.client import send_to_dpd
from lockers.lpexpress.client import send_to_lpexpress
from lockers.omniva.client import send_to_omniva
from notifications.services.customer import email_order_shipped


logger = logging.getLogger(__name__)


def send_to_carrier(order):
    if order.status == "registered":
        logger.warning(f"[AUDIT] Attempt to registrate Order={order.id}")
        return

    provider = order.locker_company

    logger.info(f"[AUDIT] Start registrating Order={order.id} via {provider}")

    try:
        if provider == "omniva":
            response = send_to_omniva(order)

        elif provider in ["dpd", "lpexpress"]:
            raise Exception(f"{provider} not implemented yet")

        # elif provider == "dpd":
        #     response = send_to_dpd(order)

        # elif provider == "lpexpress":
        #     response = send_to_lpexpress(order)

        else:
            raise Exception(f"Unknown provider: {provider}")

        logger.info(
            f"[AUDIT] {provider} response Order={order.id} status={response.status_code}"
        )

        if response.status_code != 200:
            raise Exception(f"{provider} error: {response.text}")

        shipment = create_shipment(order, provider, response.json())

        email_order_shipped(order, shipment)

        order.status = "registered"
        order.error_message = None
        order.save(update_fields=["status", "error_message"])

        logger.info(f"[AUDIT] Order={order.id} registered successfully via {provider}")

    except Exception as e:
        logger.error(f"[AUDIT] Registracing failed Order={order.id}: {e}")

        order.status = "shipping_error"
        order.error_message = str(e)
        order.save(update_fields=["status", "error_message"])


def get_all_lockers(country):
    logger.info(f"Fetching all lockers for {country}")

    omniva = get_omniva_lockers(country)
    dpd = False


    lockers = []

    if omniva:
        lockers.extend(omniva)
    else:
        logger.warning("Omniva returned 0 lockers")

    if dpd:
        lockers.extend(dpd)
    else:
        logger.warning("DPD returned 0 lockers")

    if not lockers:
        logger.error(f"No lockers available for {country}")

    return lockers


def create_shipment(order, provider, response_json):
    parsed = parse_provider_response(provider, response_json)
    label_url = build_barcode_url(provider, parsed.get("barcode"))


    shipment = Shipment.objects.create(
        order = order,
        provider = provider,
        shipment_id=parsed["partner_shipment_id"],
        tracking_number=parsed.get("barcode"),
        label_url = label_url
    )
    
    return shipment

