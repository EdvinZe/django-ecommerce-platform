from django import forms
from users.utils import validate_real_email
from .models import ContactMessage


class ContactForm(forms.ModelForm):

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]

    def clean_email(self): 
        email = self.cleaned_data.get("email") 
        return validate_real_email(email)