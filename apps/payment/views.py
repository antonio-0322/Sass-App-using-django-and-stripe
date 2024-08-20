import datetime
import logging

from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import BaseAPIException, BaseNotFoundError
from apps.payment.models import Plan, Subscription
from apps.payment.serializers import PlanSerializer
from apps.payment.stripe.services import CheckoutService, WebhookService
from apps.payment.utils import user_subscribes_to_plan, sync_user_data_with_plan_limits, create_pending_subscription, \
    activate_user_subscription, deactivate_user_subscriptions
from apps.user.utils import get_user_by_stripe_customer_id


class PlanListAPIView(ListAPIView):
    serializer_class = PlanSerializer
    permission_classes = (AllowAny, )
    queryset = Plan.objects.filter(active=True).all()


class GetCheckoutSessionAPIView(APIView):
    def get(self, request, plan_id):
        """
           API view for retrieving a checkout session.
           This view receives a GET request to retrieve a checkout session for the specified plan.
           It retrieves the plan object, verifies the existence of a Stripe customer ID for the requesting user,
           checks if the plan is chargeable, and creates a payment link using the CheckoutService.
           Parameters:
           - request: The HTTP request object containing the user information.
           - plan_id: The ID of the plan for which the checkout session is requested.
           Returns:
           - Response: An HTTP response containing the payment link for the checkout session.
           Raises:
           - BaseAPIException: If there is no created customer for the user in Stripe or if the plan's amount due is zero.
        """
        plan = Plan.objects.get(pk=plan_id)
        customer_id = request.user.stripe_customer_id
        if not customer_id:
            raise BaseAPIException("There is no created customer for this user in stripe, please contact support")
        if not plan.is_chargeable:
            raise BaseAPIException("The Checkout Session's total amount due cannot be zero in payment mode.")

        subscription = create_pending_subscription(user=request.user, plan=plan)
        res = CheckoutService().create_payment_link(
            price_id=plan.stripe_price_id,
            customer_id=customer_id,
            subscription_id=subscription.pk
        )

        return Response(res)


class SubscribeToFreePlanAPIView(APIView):
    """
        API view for subscribing a user to a free plan.
        This view receives a POST request to subscribe a user to a free plan. It creates a subscription for the user with the
        specified free plan and deactivates any existing subscriptions for the user.

        Methods:
        - post: Handles the POST request and subscribes the user to the free plan.
        """

    def post(self, request):
        plan = Plan.objects.get(amount=0)
        if request.user.has_used_free_subscription:
            raise PermissionDenied(detail="You can subscribe to free plan only once")
        user_subscribes_to_plan(user=request.user, plan=plan)

        return Response(status=status.HTTP_201_CREATED)


class TestAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        sync_user_data_with_plan_limits(request.user)
        return Response()


class CheckoutCompletedWebhookAPIView(APIView):
    """
        API view for handling the checkout completed webhook received from stripe.
        This view receives a POST request containing information about a completed checkout event.
        It verifies the webhook signature, retrieves the relevant data, and creates subscription for user.

        Permissions:
        - AllowAny: All users, authenticated or anonymous, can access this view.

        Methods:
        - post: Handles the POST request and processes the checkout completion.
        """
    permission_classes = (AllowAny, )

    @transaction.atomic
    def post(self, request):
        """
           Handle the POST request and process the checkout completion.
           Parameters:
           - request: The HTTP request object containing the webhook data.
           Returns:
           - Response: An HTTP response indicating the status of the request.
           Raises:
           - ValueError
           - stripe.error.SignatureVerificationError
       """
        WebhookService().verify_signature(request)
        logger = logging.getLogger('webhooks')
        logger.info(f"Received stripe webhook: , {request.data}")

        customer_id = request.data['data']['object']['customer']
        user = get_user_by_stripe_customer_id(customer_id)
        subscription_id = request.data['data']['object']['metadata']['subscription_id']
        webhook_id = request.data['id']
        created_at = datetime.datetime.fromtimestamp(request.data['created']) 
        subscription = Subscription.objects.get(pk=subscription_id)

        if not subscription:
            logger.error(f"Stripe webhook, could not find subscription: id = {subscription_id} ")
            raise BaseNotFoundError(f"Subscription isn't exists:{subscription_id}")

        later_created_subscription = user.subscriptions.filter(
            stripe_webhook_created_at__gt=created_at,
            user=user,
            active=True
        ).exists()

        if later_created_subscription:
            # this means user has created subscription later and we don't need owerride it
            logger.info(
                f"Stripe webhook,Received webhook after user has created another subscription:id={subscription_id}"
            )
            return Response(status=status.HTTP_200_OK)

        deactivate_user_subscriptions(user)
        activate_user_subscription(
            subscription=subscription,
            stripe_webhook_id=webhook_id,
            created_at=created_at
        )

        sync_user_data_with_plan_limits(user)

        return Response(status=status.HTTP_200_OK)
