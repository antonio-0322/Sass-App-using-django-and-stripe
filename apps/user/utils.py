import datetime
import logging
import secrets
from typing import Union

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException

from apps.core.exceptions import BaseNotFoundError, BaseAPIException
from apps.user.enums import EmailType, EMAIL_TEMPLATES
from apps.user.models import UserEmailVerificationCode, User


def create_verification_code(email: str) -> UserEmailVerificationCode:
    """
        generates new verification code for user
        which will expire in 10 minutes
        before that we delete all previous codes for that user
    """
    delete_all_verification_codes_for_user(email)

    code = generate_verification_code()

    return UserEmailVerificationCode.objects.create(
        email=email,
        code=code,
        expires_in=datetime.datetime.now() + datetime.timedelta(hours=24)
    )


def delete_all_verification_codes_for_user(email: str):
    return UserEmailVerificationCode.objects.filter(email=email).delete()


def generate_verification_code() -> str:
    """
        Generate unique hash
        :return: string
    """
    url_hash = secrets.token_urlsafe()

    while UserEmailVerificationCode.objects.filter(code=url_hash).exists():
        url_hash = secrets.token_urlsafe()

    return url_hash


def verify_code(email: str, code: str):
    """
       Verifies code against a given email address.

       Args:
           email (str): The email address to verify.
           code (str): The verification code to check.
       Raises:
           BaseNotFoundError: If the verification code is wrong or does not exist.
           BaseAPIException: If the verification link is expired.
       """

    row = UserEmailVerificationCode.objects.filter(
        code=code,
        email=email
    ).first()

    if not row:
        raise BaseNotFoundError(f"There was an error verifying your email address. Please request a new link.")

    if row.expires_in < timezone.now():
        raise BaseAPIException(detail=f"The verify link sent to {email} is expired.")


def send_verification_email(user: User, code: UserEmailVerificationCode, email_type: EmailType):
    """
        This function sends a verification code to an email address.
        Parameters:
            user (User): The email address to send the verification code to.
            code (UserEmailVerificationCode): The code to be sent.
            email_type: (EmailType): based on type will be decided email template
        Raises:
            APIException: If sending the email fails.
        """
    logo_url = f'{settings.BASE_URL}static/images/logo.png'
    action = 'email-verify' if email_type == EmailType.ACTIVATE_ACCOUNT.value else 'reset-password'
    verification_url = f'{settings.BASE_FRONTEND_URL}auth/{action}?email={user.email}&code={code.code}'
    message = render_to_string(
        f"email/{EMAIL_TEMPLATES[email_type]}",
        {
            "verification_url": verification_url,
            "logo_url": logo_url,
            "user": user
        }
    )

    try:
        email = send_mail(
            subject="AutoSubmit, Verify your email",
            from_email=settings.DEFAULT_FROM_EMAIL,
            message='',
            recipient_list=[user.email],
            html_message=message
        )
    except Exception as e:
        logging.getLogger('file').error(e)
        raise APIException(_("Verification sending email has been failed please try again later"))


def get_user_by_stripe_customer_id(customer_id: str) -> Union[User, None]:
    return User.objects.filter(stripe_customer_id=customer_id).first()
