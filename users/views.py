import logging
from django.contrib import auth, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from cart.models import Cart
from .forms import UserRegistrationForm, UserLoginForm, UserProfileChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin

logger = logging.getLogger(__name__)

def registration(request):
    if request.method == "POST":
        form = UserRegistrationForm(data=request.POST)

        if form.is_valid():
            form.save()

            session_key = request.session.session_key

            user = form.instance
            auth.login(request, user)

            if session_key:
                Cart.objects.filter(session_key=session_key).update(user=user)

            messages.success(request, f"Jūs {user.username} sėkmingai prisijungėte prie savo paskyros")
            logger.info(f"[AUDIT] New user registered id={user.id}")
            return redirect('main')

    else:
        form = UserRegistrationForm()

    context = {"title": "Registacija", "form": form}

    return render(request, "users/registracion.html", context)




def login(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user:
                auth.login(request, user)
                messages.success(request, f"Jūs {user.username} sėkmingai prisijungėte prie savo paskyros")
                return redirect('main')

    else:
        form = UserLoginForm()


    context = {"title": "autorizacija", "form": form}

    return render(request, "users/login.html", context)



@login_required
def profile(request):
    if request.method == "POST":
        form = UserProfileChangeForm(data=request.POST, instance = request.user, files = request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, f"Jūs {request.user.username} sėkmingai atnaujinote savo profilį.")
            return redirect('main')

    else:
        form = UserProfileChangeForm(instance = request.user)


    context = {"title": "profilis", "form": form}

    return render(request, "users/profile.html", context)



@login_required
def logout(request):
    messages.success(request, f"Jūs {request.user.username} sėkmingai astsijungėte nuo savo paskyros")
    auth.logout(request)
    return redirect('main')


class MyPasswordChangeView(LoginRequiredMixin ,PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('main')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Slaptažodžio keitimas'
        return context
    