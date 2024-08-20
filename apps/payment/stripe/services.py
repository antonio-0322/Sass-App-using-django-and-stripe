import logging

from django.conf import settings
import stripe
from rest_framework.request import Request
from stripe.error import InvalidRequestError

from apps.core.exceptions import BaseAPIException


class StripeClient:
    def __init__(self, client_secret: str = settings.STRIPE_SECRET_KEY):
        self.client_secret = client_secret
        self.client = stripe
        self.client.api_key = self.client_secret


class PlanService(StripeClient):
    def __init__(self):
        super().__init__()
        self.api = self.client.Plan

    def list_all_plans(self, *args, **kwargs):
        return self.api.list(*args, **kwargs)


class CustomerService(StripeClient):
    def __init__(self):
        super().__init__()
        self.api = self.client.Customer

    def create_customer(self, email):
        try:
            return self.api.create(
                email=email
            )
        except InvalidRequestError as e:
            raise BaseAPIException(detail="Stripe Customer creation has been failed")


class PaymentLinkService(StripeClient):
    def __init__(self):
        super().__init__()
        self.api = self.client.PaymentLink

    def create_payment_link(self, price_id: str):
        try:
            return self.api.create(
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    },
                ],
            )
        except InvalidRequestError as e:
            logging.getLogger('common').error(e)
            raise BaseAPIException(detail="Payment link creation has been failed")


class CheckoutService(StripeClient):
    success_url = settings.STRIPE_SUCCESS_PAYMENT_REDIRECT_URL
    cancel_url = settings.STRIPE_PAYMENT_CANCEL_URL

    def __init__(self):
        super().__init__()
        self.api = self.client.checkout

    def create_payment_link(self, price_id: str, customer_id: str, subscription_id):
        try:
            return self.api.Session.create(
                success_url=self.success_url,
                cancel_url=self.cancel_url,
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    },
                ],
                invoice_creation={
                    "enabled": True
                },
                metadata={
                    "subscription_id": subscription_id
                },
                mode="payment",
                customer=customer_id,
                allow_promotion_codes=True
            )
        except InvalidRequestError as e:
            logging.getLogger('common').error(e)
            raise BaseAPIException(detail="Payment link creation has been failed")


class SubscriptionService(StripeClient):
    def __init__(self):
        super().__init__()
        self.api = self.client.Subscription

    def get_customer_subscription(self, customer_id):
        try:
            return self.api.list(
                customer=customer_id,
                status="active"
            )
        except InvalidRequestError as e:
            raise BaseAPIException(detail="Payment link creation has been failed")


class WebhookService(StripeClient):
    def __init__(self):
        super().__init__()
        self.api = self.client.Webhook

    def verify_signature(self, request: Request):
        payload = request.body
        sig_header = request.headers['STRIPE_SIGNATURE']
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_CHECKOUT_COMPLETED_KEY
            )
        except ValueError as e:
            # Invalid payload
            raise e
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise e
