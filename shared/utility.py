#email check pythonn
from rest_framework.exceptions import ValidationError
import re
email_regex=re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
phone_regex=re.compile(r"^9\d{12$")

def check_email_phone(email_or_phone):
    if re.fullmatch(email_regex,email_or_phone):
        email_or_phone='email'

    elif re.fullmatch(phone_regex,email_or_phone):
        email_or_phone='phone'
    else:
        data={
            'succes':False,
            "message":"Email or phone number is invalid."
        }
    return email_or_phone
