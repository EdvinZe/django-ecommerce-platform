from email_validator import validate_email, EmailNotValidError
from django.core.exceptions import ValidationError

def validate_real_email(value):
    try:
        validate_email(value, check_deliverability=True)
    except EmailNotValidError:
        raise ValidationError("Įvestas el. pašto adresas yra neteisingas.")
    return value



def get_or_create_session_key(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    return session_key