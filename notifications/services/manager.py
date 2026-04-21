from django.core.mail import send_mail
from notifications.services.email import log_email_sent, send_email
from site_settings.services import get_site_settings

Company = get_site_settings()

def email_manager_from_contact_us(contact):
    send_email(
        subject="Nauja žinutė iš kliento",
        to=Company.support_email,
        template="notifications/emails/manager/site_notification.html",
        ctx={
            "contact": contact,
        },
        email_type="contact_message",
    )