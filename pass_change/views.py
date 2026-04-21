from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.conf import settings
from django.shortcuts import render
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()



class MyPasswordResetView(PasswordResetView):
    template_name = 'pass_change/forgot_pass_email.html'
    success_url = reverse_lazy('email_instruction')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Slaptažodžio atstatymas - elektroninis paštas'
        return context
    

class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'pass_change/forgot_pass_sentcode.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Slaptažodžio atstatymas - instrukcija'
        return context


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'pass_change/forgot_pass_changepass.html'
    success_url = reverse_lazy('password_reset_complete')

    def dispatch(self, request, *args, **kwargs):
        self.user = self.get_user(kwargs["uidb64"])

        if self.user and self.user.is_manager:
            messages.warning(self.request, "Demo admin vartotojui negalima keisti slaptažodžio")
            return redirect('main')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Slaptažodžio atstatymas - naujas slaptažodis'
        return context

    
class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'pass_change/forgot_pass_passchanged.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Slaptažodžio atstatymas - Pabaiga'
        return context
    

class DemoPasswordResetView(PasswordResetView):

   def form_valid(self, form):
    email = form.cleaned_data["email"]

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return super().form_valid(form)

    if user.is_manager:
        messages.warning(self.request, "Demo vartotojui negalima atstatyti slaptažodžio")
        return redirect("login") 

    if settings.DEMO_MODE:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_url = self.request.build_absolute_uri(
            reverse("password_reset_confirm", kwargs={
                "uidb64": uid,
                "token": token
            })
        )

        return render(self.request, "pass_change/demo_reset_link.html", {
            "reset_url": reset_url
        })

    return super().form_valid(form)
        
        