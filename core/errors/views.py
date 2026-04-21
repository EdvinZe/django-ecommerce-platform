from django.shortcuts import render


def error_404(request, exception):
    return render(
        request,
        "errors/error.html",
        {
            "code": 404,
            "message": "Puslapis nerastas 😢",
        },
        status=404,
    )


def error_500(request):
    return render(
        request,
        "errors/error.html",
        {
            "code": 500,
            "message": "Serverio klaida 🔧",
        },
        status=500,
    )

def error_403(request, exception):
    return render(request, "errors/error.html", {
        "code": 403,
        "message": "Prieiga draudžiama"
    }, status=403)