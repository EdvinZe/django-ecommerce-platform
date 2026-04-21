from django.urls import path
from pass_change.views import (
    DemoPasswordResetView,
    MyPasswordResetDoneView,
    MyPasswordResetView,
    MyPasswordResetCompleteView,
    MyPasswordResetConfirmView,
)


urlpatterns = [
    # path(
    #     "reset/",
    #     MyPasswordResetView.as_view(
    #         html_email_template_name="pass_change/forgot_pass_message.html"
    #     ),
    #     name="get_email",
    # ),
    path("reset/done/", MyPasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "reset/<uidb64>/<token>/",
        MyPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/complete/",
        MyPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
    "password-reset/",
    DemoPasswordResetView.as_view(
        template_name="pass_change/forgot_pass_email.html",
        html_email_template_name="pass_change/forgot_pass_message.html",
    ),
    name="get_email",
    ),
]
