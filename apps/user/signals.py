import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from pydparser import ResumeParser

from apps.payment.stripe.services import CustomerService
from apps.user.enums import EmailType, SignupTypes
from apps.user.models import User, UserResume
from apps.user.services import ResumeParserService
from apps.user.utils import send_verification_email, create_verification_code


@receiver(post_save, sender=User)
def post_create_handler(sender, instance, created, **kwargs):
    if created:
        if instance.signup_type == SignupTypes.EMAIL.value:
            send_verification_email(
                user=instance,
                code=create_verification_code(email=instance.email),
                email_type=EmailType.ACTIVATE_ACCOUNT.value
            )

        customer = CustomerService().create_customer(email=instance.email)
        instance.stripe_customer_id = customer.id
        instance.save()


@receiver(post_save, sender=UserResume)
def post_create_(sender, instance, created, **kwargs):
    logging.getLogger('common').info('UserResume post_create_handler')
    if created:
        ResumeParserService(instance).save_parsed_data()


