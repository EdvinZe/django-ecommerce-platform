from django.urls import path
from pages.views import AboutUsView, ContactsView, PrivacyView, TermsView

urlpatterns = [
    path('apie_mus/', AboutUsView.as_view(), name='apie_mus'),
    path('kontaktai/', ContactsView.as_view(), name='kontaktai'),
    path("terms/", TermsView.as_view(), name="terms"),
    path("privacy/", PrivacyView.as_view(), name="privacy"),
]
