from django.urls import path
from lockers.views import all_lockers, shipment_barcode_view

urlpatterns = [
    path("all/", all_lockers, name="all_lockers"),
    path(
        "shipment/<str:provider>/<str:barcode>/",
        shipment_barcode_view,
        name="shipment-barcode",
    ),
]
