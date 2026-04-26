import logging
from django.shortcuts import render
from django.views.generic import TemplateView, FormView

from notifications.services.customer import email_contact_autoreply
from .models import GalleryImage
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ContactForm
from notifications.services.manager import email_manager_from_contact_us
from .services import get_gallery

logger = logging.getLogger(__name__)


class AboutUsView(TemplateView):
    template_name = 'pages/apiemus.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = "Braškės Iš Širdies - Apie mus"
        context["mapinput"] = "True"

        images = get_gallery()

        context["main_image"] = images[0] if images else None
        context["gallery_images"] = images[1:] if len(images) > 1 else []

        return context


class ContactsView(FormView):
    template_name = "pages/contacts.html"
    form_class = ContactForm
    success_url = reverse_lazy("main")


    def form_valid(self, form):
        contact_message = form.save()

        try:
            email_manager_from_contact_us(contact_message)
        except Exception as e:
            logger.error(f"Contact email to manager failed: {e}")

        try:
            email_contact_autoreply(contact_message)
        except Exception as e:
            logger.error(f"Contact autoreply email failed: {e}")

        messages.success(
            self.request,
            message="Žinutė sėkmingai išsiųsta!"
        )

        return super().form_valid(form)
    

class TermsView(TemplateView):
    template_name = "pages/terms.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = "Taisyklės ir sąlygos"
        context["updated"] = "2026"

        return context


class PrivacyView(TemplateView):
    template_name = "pages/privacy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = "Privatumo politika"
        context["updated"] = "2026"

        return context