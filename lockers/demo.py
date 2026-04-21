from lockers.services import create_shipment
import logging

logger = logging.getLogger(__name__)


def demo_send_to_carrier(order):
    provider = order.locker_company

    logger.info(f"[DEMO] Sending Order={order.id} via {provider}")

    fake_payload = {
    "resultCode": "OK",
    "savedShipments": [
        {
            "barcode": f"DEMO-{order.id}",
            "partnerShipmentId": str(order.id),
            "clientItemId": str(order.id),
        }
    ]
}

    shipment = create_shipment(order, provider, fake_payload)

    order.status = "registered"
    order.error_message = None
    order.save(update_fields=["status", "error_message"])

    logger.info(f"[DEMO] Order={order.id} registered successfully")

    return shipment