from django.urls import path
from payments.views import stripe_payment, payment_success, payment_cancel, stripe_webhook

urlpatterns = [
    path("create_stripe_session/<int:order_id>/", stripe_payment, name ="stripe_payment"),
    path("success/", payment_success, name="payment_success"),
    path("cancel/", payment_cancel, name="payment_cancel"),
    path("stripe/webhook/", stripe_webhook, name="stripe_webhook"),
]