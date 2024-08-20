from django.core.management.base import BaseCommand
import random

from apps.payment.models import Plan, PlanOption

DEFAULT_PLANS = [
    {
        "name": "Free",
        "slug": Plan.PlanSlugs.FREE,
        "label": "Try before you buy",
        "amount": 0,
        'image': 'images/free_plan.svg',
        "options": [
            {
                "type": PlanOption.PlanOptionTypes.JOB_APPLICATIONS,
                "value": 2,
                "text": "<b>4</b> Job applications"
            },
            {
                "type": PlanOption.PlanOptionTypes.JOB_APPLICATIONS_PER_DAY,
                "value": 2,
                "text": "<b>2</b>  Job applications/day"
            },
            {
                "type": PlanOption.PlanOptionTypes.JOB_TITLE,
                "value": 1,
                "description": "Example<br><b>Data Analyst</b>",
                "text": "<b>1</b> Job Title"
            },
        ]
    },
    {
        "name": "Pro",
        "slug": Plan.PlanSlugs.PRO,
        "label": "I am actively searching",
        'image': 'images/pro_plan.svg',
        "amount": 49.99,
        "is_favorite": False,
        "options": [
            {
                "type": PlanOption.PlanOptionTypes.JOB_APPLICATIONS,
                "value": 250,
                "text": "<b>250</b> Job applications"
            },
            {
                "type": PlanOption.PlanOptionTypes.JOB_APPLICATIONS_PER_DAY,
                "value": 20,
                "text": "Up to <b>20</b> applications/day"
            },
            {
                "type": PlanOption.PlanOptionTypes.JOB_TITLE,
                "value": 3,
                "description": "Example<br><b>Data Analyst, Data Engineer,<br> Data Scientist</b>",
                "text": "<b>3</b> Job Titles"
            },
            {
                "type": PlanOption.PlanOptionTypes.FILTER_OUT_COMPANIES,
                "text": "Filter out companies"
            },
            {
                "type": PlanOption.PlanOptionTypes.JOB_APPLICATIONS_TRACKER,
                "text": "Job submission tracker"
            },
        ]
    },
    {
        "name": "Advanced",
        "slug": Plan.PlanSlugs.ADVANCED,
        "label": "I need a job now",
        "amount": 79.99,
        'image': 'images/advanced_plan.svg',
        "is_favorite": False,
        "options": [
            {
                "type": PlanOption.PlanOptionTypes.JOB_APPLICATIONS,
                "value": 500,
                "text": "<b>500</b> Job applications"
            },
            {
                "type": PlanOption.PlanOptionTypes.JOB_APPLICATIONS_PER_DAY,
                "value": 30,
                "text": "Up to <b>30</b> applications/day"
            },
            {
                "type": PlanOption.PlanOptionTypes.JOB_TITLE,
                "value": 100000, # unlimited
                "text": "<b>Unlimited</b> Job Titles",
                "description": "Example<br><b>Data Analyst, Data Engineer,<br> Data Scientist</b>",
            },
            {
                "type": PlanOption.PlanOptionTypes.FILTER_OUT_COMPANIES,
                "text": "Filter out companies"
            },
            {
                "type": PlanOption.PlanOptionTypes.JOB_APPLICATIONS_TRACKER,
                "text": "Job submission tracker"
            },
        ]
    }
]


class Command(BaseCommand):
    help = "seed default subscription plans"

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        run_seed()
        self.stdout.write('done.')


def clear_data():
    """Deletes all the table data"""
    Plan.objects.all().delete()


def run_seed():
    """ Seed database based on mode
    :param mode: refresh / clear
    :return:
    """
    for plan in DEFAULT_PLANS:
        options = plan.pop('options')
        plan, created = Plan.objects.update_or_create(slug=plan['name'], defaults=plan)

        for plan_option in options:
            PlanOption.objects.update_or_create(type=plan_option['type'], plan_id=plan.id, defaults=plan_option)


