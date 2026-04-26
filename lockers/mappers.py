import requests
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from lockers.utils import get_dpd_token
from core.cache import get_or_set_cache
import logging
from .api_configs import OmnivaConfig, DPDConfig

logger = logging.getLogger(__name__)

def omniva_lockers(country):
    logger.info(f"Fetching Omniva lockers for {country}")

    try:
        response = requests.get(
            OmnivaConfig.LOCKERS_URL,
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

    except Exception as e:
        logger.error(f"Omniva request failed: {e}")
        return []

    lockers = []

    for item in data:
        if item.get("TYPE") != "0":
            continue

        if item.get("A0_NAME") != country:
            continue

        try:
            lockers.append({
                "id": item["ZIP"],
                "lat": float(item["Y_COORDINATE"]),
                "lng": float(item["X_COORDINATE"]),
                "name": item["NAME"],
                "provider": "omniva",
            })
        except Exception as e:
            logger.warning(f"Omniva parsing error: {e}")

    logger.info(f"Omniva lockers fetched: {len(lockers)}")

    return lockers

def get_omniva_lockers(country):
    return get_or_set_cache(
        key=f"omniva_{country}",
        fetch_func=lambda: omniva_lockers(country),
    )


def dpd_lockers(country):
    logger.info(f"Fetching DPD lockers for {country}")

    token = get_dpd_token()

    try:
        response = requests.get(
            f"{DPDConfig.LOCKERS_URL}",
            params={"countryCode": country},
            headers={
                "Authorization": f"Bearer {token}", 
                "Accept": "application/json+fulldata",
            },
            timeout=5,
        )

        logger.info(f"DPD response status: {response.status_code}")

        response.raise_for_status()
        data = response.json()

    except Exception as e:
        logger.error(f"DPD request failed: {e}")
        return []

    if isinstance(data, dict):
        data = data.get("items") or data.get("data") or []

    lockers = []

    for item in data:
        address = item.get("address") or {}
        latlng = address.get("latLong")

        if not latlng:
            continue

        try:
            if isinstance(latlng, str):
                latlng = latlng.split(",")

            lockers.append({
                "id": item.get("id"),
                "lat": float(latlng[0]),
                "lng": float(latlng[1]),
                "name": item.get("name") or "DPD Locker",
                "provider": "dpd",
            })
        except Exception as e:
            logger.warning(f"DPD parsing error: {e}")

    logger.info(f"DPD lockers fetched: {len(lockers)}")

    return lockers

def get_dpd_lockers(country):
    return get_or_set_cache(
        key=f"dpd_{country}",
        fetch_func=lambda: dpd_lockers(country),
    )

def lp_express_lockers(country):
    if country != "LT":
        return []

    try:
        response = requests.get(
            "https://www.lpexpress.lt/terminalai",
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"LP Express request failed: {e}")
        return []

    lockers = []

    for item in data:
        if not item.get("active", True):
            continue

        lat = item.get("latitude")
        lng = item.get("longitude")

        if not lat or not lng:
            continue

        try:
            lockers.append({
                "id": item.get("terminalId"),
                "lat": float(lat),
                "lng": float(lng),
                "name": item.get("name") or "LP EXPRESS",
                "provider": "lp_express",
            })
        except Exception as e:
            logger.warning(f"LP Express parsing error: {e}")

    logger.info(f"LP Express lockers fetched: {len(lockers)}")

    return lockers
