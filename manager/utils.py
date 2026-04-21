from functools import wraps
from django.shortcuts import redirect

def manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return redirect("login")

        if not user.is_superuser and not getattr(user, "is_manager", False):
            return redirect("main")

        return view_func(request, *args, **kwargs)

    return _wrapped_view