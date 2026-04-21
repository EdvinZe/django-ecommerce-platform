from django.conf import settings
from .email import send_email, log_email_sent


def email_order_paid(order):
    send_email(
        subject=f"Užsakymas #{order.id} apmokėtas 💰",
        to=order.email,
        template="notifications/emails/customer/order_paid.html",
        ctx={
            "order": order,
        },
        order=order,
        email_type="order_paid",
    )

def email_order_shipped(order, shipment):
    tracking_code = shipment.tracking_number

    tracking_url = None
    if tracking_code:
        if shipment.provider == "omniva":
            tracking_url = f"https://www.mano.omniva.lt/track/{tracking_code}"
        # elif shipment.provider == "dpd":
        #     tracking_url = f"https://tracking.dpd.de/status/en_US/parcel/{tracking_code}"

    send_email(
        subject=f"Užsakymas #{order.id} išsiųstas 📦",
        to=order.email,
        template="notifications/emails/customer/order_shipped.html",
        ctx={
            "order": order,
            "tracking_code": tracking_code,
            "tracking_url": tracking_url,
        },
        order=order,
        email_type="order_shipped",
    )

def email_payment_failed(order):
    send_email(
        subject=f"Mokėjimas nepavyko – Užsakymas #{order.id}",
        to=order.email,
        template="notifications/emails/customer/order_fail.html",
        ctx={
            "order": order,
            "retry_url": f"{settings.SITE_URL}/orders/order_form/",
        },
        order=order,
        email_type="order_failed",
    )

def email_contact_autoreply(contact):
    send_email(
        subject="Gavome jūsų žinutę ✉️",
        to=contact.email,
        template="notifications/emails/contact/autoreply.html",
        ctx={
            "contact": contact,
        },
        email_type="contact_autoreply",
    )