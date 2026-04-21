from lockers.services import get_all_lockers
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Shipment

def all_lockers(request):
    country =  "LT"
    return JsonResponse(get_all_lockers(country), safe=False)
    
    
def shipment_barcode_view(request, provider, barcode):
    shipment = get_object_or_404(
        Shipment,
        provider=provider,
        tracking_number=barcode,
    )

    return render(
        request,
        "lockers/barcode.html",
        {"shipment": shipment},
        )