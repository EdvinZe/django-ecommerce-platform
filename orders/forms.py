from django import forms
from orders.models import Order
from users.utils import validate_real_email

class OrderForm(forms.ModelForm):

    accept_terms = forms.BooleanField(
        required=True,
        error_messages={
            "required": "Turite sutikti su taisyklėmis"
        }
    )

    class Meta:
        model = Order
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "delivery_method",
            "payment_method",
            "locker_company",
            "locker",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        return validate_real_email(email)