import requests
def parse_omniva_response(response_json):
    shipments = response_json.get("savedShipments", [])

    if not shipments:
        return None

    shipment = shipments[0]

    return {
        "barcode": shipment["barcode"],
        "partner_id": shipment["clientItemId"],
        "provider": "Omniva",
    }

