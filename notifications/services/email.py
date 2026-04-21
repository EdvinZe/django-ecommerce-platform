from django.utils import timezone
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from notifications.models import EmailLog
from site_settings.services import get_site_settings

logger = logging.getLogger(__name__)

def send_email(*, subject, to, template, ctx, order=None, email_type=None):
    try:
        html_body = render_to_string(template, {
            **ctx,
            "site_settings": get_site_settings(),
            "now": timezone.now(),
            })

        send_mail(
            subject=subject,
            message="", 
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to],
            html_message=html_body, 
            fail_silently=False,
        )

        logger.info(f"[AUDIT] Email sent type={email_type} Order={order.id if order else None}")

        if order and email_type:
            log_email_sent(order, email_type, to)

    except Exception as e:
        logger.error(
            f"[AUDIT] Email failed type={email_type} Order={order.id if order else None}: {e}"
        )
        raise
    

def email_customer(order, template, subject):
    send_email(
        subject=subject,
        to=order.email,
        template=template,
        ctx={"order": order},
        order=order,
        email_type="customer",
    )

def email_manager(order, shipment, template, subject):
    send_email(
        subject=subject,
        to=settings.MANAGER_EMAIL,
        template=template,
        ctx={
            "order": order.id,
            "shipment": shipment,
        },
        order=order,
        email_type="manager",
    )

def log_email_sent(order, email_type, to):
    EmailLog.objects.create(
        order=order,
        email_type=email_type,
        to=to,
    )
