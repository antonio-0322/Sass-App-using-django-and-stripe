import stripe
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.payment.models import Plan


class Command(BaseCommand):
    help = "Update plans, define stripe plan id"

    def handle(self, *args, **options):
        self.stdout.write('sync with stripe')
        stripe.api_key = settings.STRIPE_SECRET_KEY

        stripe_plans = stripe.Product.list(active=True)

        for plan in stripe_plans['data']:
            Plan.objects.filter(name=plan['name']).update(stripe_price_id=plan['default_price'])

        self.stdout.write('done.')



