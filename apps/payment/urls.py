from django.urls import path

from apps.payment.views import *

urlpatterns = [
    path('plans/', PlanListAPIView.as_view()),
    path('get-checkout-link/<int:plan_id>/', GetCheckoutSessionAPIView.as_view()),
    path('subscribe-to-free-plan/', SubscribeToFreePlanAPIView.as_view()),
    path('test/', TestAPIView.as_view()),
    path('webhook/checkout-completed/', CheckoutCompletedWebhookAPIView.as_view()),
]
