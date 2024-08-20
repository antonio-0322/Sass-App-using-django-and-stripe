from enum import Enum

from django.db.models import TextChoices


class EmailType(Enum):
    ACTIVATE_ACCOUNT = 'activate_account'
    VERIFY_EMAIL = 'verify_email'
    RESET_PASSWORD = 'reset_password'


class SignupTypes(TextChoices):
    GOOGLE = 'google', 'Google'
    EMAIL = 'email', 'Email'


EMAIL_TEMPLATES = {
    EmailType.VERIFY_EMAIL.value: 'verify_email.html',
    EmailType.ACTIVATE_ACCOUNT.value: 'activate_account.html',
    EmailType.RESET_PASSWORD.value: 'reset-password.html'
}


GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://accounts.google.com/o/oauth2/v2/auth?'
