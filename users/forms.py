from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from users.utils import validate_real_email
from .models import User
from email_validator import validate_email, EmailNotValidError

class UserRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'phone', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["phone"].error_messages["invalid"] = "Neteisingas telefono numeris"
        self.fields["email"].error_messages["invalid"] = "Neteisingas el. pašto adresas"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        return validate_real_email(email)



class UserLoginForm(AuthenticationForm):
    class Meta(AuthenticationForm):
        model = User


class UserProfileChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('email', 'phone', 'first_name', 'last_name', 'username', 'image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["phone"].error_messages["invalid"] = "Neteisingas telefono numeris"
        self.fields["email"].error_messages["invalid"] = "Neteisingas el. pašto adresas"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        return validate_real_email(email)