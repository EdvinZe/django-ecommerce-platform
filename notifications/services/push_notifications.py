import json
import logging
from urllib.parse import urlparse
from django.conf import settings
from pywebpush import WebPushException, webpush

from notifications.models import PushSubscription

logger = logging.getLogger(__name__)

def send_push():
    subs = PushSubscription.objects.all()

    payload = json.dumps({
        "title": "🔥 Naujas užsakymas!",
        "body": "Patikrinkite užsakymus",
        "url": "/manager/orders/"
    })

    errors = set()

    for sub in subs:
        try:
            parsed = urlparse(sub.endpoint)

            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth,
                    },
                },
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": settings.VAPID_EMAIL,
                    "aud": f"{parsed.scheme}://{parsed.netloc}",
                },
            )

        except WebPushException as e:
            error_text = str(e)

            if (
                (e.response and e.response.status_code in [404, 410])
                or "410 Gone" in error_text
                or "expired" in error_text
            ):
                sub.delete()
                continue

            errors.add(error_text)

        except Exception as e:
            errors.add(str(e))

    for err in errors:
        logger.error(f"Push error: {err}")