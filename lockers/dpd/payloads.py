def payload_dpd(order):
    return {
        "senderAddress": {
            "name": "Shop Name",
            "email": "shop@example.com",
            "phone": "+37060000000",
            "street": "Shop street",
            "streetNo": "1",
            "flatNo": "None",
            "city": "Vilnius",
            "postalCode": "01100",
            "country": "LT",
        },

        "receiverAddress": {
            "name": order.first_name,
            "email": order.email,
            "phone": order.phone,
            "street": order.locker_company,
            "streetNo": "1",
            "flatNo": "None",
            "city": "None",
            "postalCode": "00000",
            "country": "None",
        },

        "receiverPickupPointId": order.locker,

        "service": {
            "serviceAlias": "DPD CLASSIC"
        },

        "parcels": [
            {
                "weight": 1.0
            }
        ],

        "shipmentReferences": [
            f"order_{order.id}"
        ]
    }