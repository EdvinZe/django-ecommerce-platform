import requests
from lockers.omniva.payloads import payload_omniva_parcel
from lockers.api_configs import OmnivaConfig

def send_to_omniva(order):
    headers = {
        "X-Integration-Agent-Id": "Developer_8206082_truskawka",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = payload_omniva_parcel(order)

    response = requests.post(
        OmnivaConfig.CREATE_SHIPMENT_URL,
        json=payload,
        auth=(OmnivaConfig.USERNAME, OmnivaConfig.PASSWORD),
        headers=headers,
        timeout=15,
    )


    return response

