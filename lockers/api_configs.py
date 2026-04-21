from django.conf import settings


class OmnivaConfig:
    USERNAME = settings.OMNIVA_USERNAME
    PASSWORD = settings.OMNIVA_PASSWORD
    CREATE_SHIPMENT_URL = f"{settings.OMNIVA_BASE_URL}/omx/shipments/business-to-client"
    LOCKERS_URL = settings.OMNIVA_LOCKERS_URL


class DPDConfig:
    USERNAME = settings.DPD_USERNAME
    PASSWORD = settings.DPD_PASSWORD
    CLIENT_ID = settings.DPD_CLIENT_ID
    TOKEN = settings.DPD_TOKEN
    BASE_URL = settings.DPD_BASE_URL
    LOCKERS_URL = f"{settings.DPD_BASE_URL}/lockers"