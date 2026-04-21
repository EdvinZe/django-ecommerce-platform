from site_settings.services import get_site_settings


def payload_omniva_parcel(order):
    Company = get_site_settings()

    return {
        "customerCode": 8206082,
        "shipments": [
            {
                "mainService": "PARCEL",
                "deliveryChannel": "PARCEL_MACHINE",
                "partnerShipmentId": f"{order.id}",
                "receiverAddressee": {
                    "personName": f"{order.get_fullname()}",
                    "contactEmail": f"{order.email}",
                    "contactMobile": f"{order.phone_number_e164()}",
                    "address": {
                        "country": "LT",
                        "offloadPostcode": f"{order.locker}",
                    },
                },
                "senderAddressee": {
                    "personName": Company.company_name,
                    "contactEmail": Company.email,
                    "contactMobile": Company.phone_number_e164(),
                    "address": {
                        "country": "LT",
                        "postcode": Company.postal_code,
                    },
                },
            }
        ],
    }