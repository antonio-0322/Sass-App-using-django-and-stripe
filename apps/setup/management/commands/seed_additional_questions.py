from django.core.management.base import BaseCommand

from apps.setup.enums import FieldType
from apps.setup.models import AdditionalQuestion


class Command(BaseCommand):
    help = "seed default questions for user to setup profile"
    ADDITIONAL_QUESTIONS = [
        # {
        #     "type": FieldType.INPUT,
        #     "title": "Phone Number",
        #     "order": 1,
        #     "is_required": True,
        # },
        {
            "type": FieldType.RADIO,
            "title": "Are you legally authorized to work in United States?",
            "order": 1,
            "is_required": True,
            "items": [
                {
                    "label": "Yes",
                    "value": "Yes"
                },
                {
                    "label": "No",
                    "value": "No"
                }
            ]
        },
        {
            "type": FieldType.NUMBER_INPUT,
            "order": 2,
            "title": "How many years of experience do you have?",
            "placeholder": "Enter the number of years",
            "is_required": True,
        },
        {
            "type": FieldType.RADIO,
            "order": 3,
            "title": "Do you now or in future require Vise Sponsorship?",
            "is_required": True,
            "items": [
                {
                    "label": "Yes",
                    "value": "Yes"
                },
                {
                    "label": "No",
                    "value": "No"
                }
            ]
        },
        {
            "type": FieldType.RADIO,
            "order": 4,
            "title": "What gender identity do you most closely identify with?",
            "items": [
                {
                    "label": "Decline to self identity",
                    "value": "Decline to self identity"
                },
                {
                    "label": "Male",
                    "value": "Male"
                },
                {
                    "label": "Female",
                    "value": "Female"
                },
            ],
        },
        {
            "type": FieldType.SELECT,
            "title": "What is your race or ethnicity?",
            "placeholder": "Choose race or ethnicity",
            "order": 5,
            "items": [
                {
                    "label": "Decline to Self Identify",
                    "value": "Decline to Self Identify"
                },
                {
                    "label": "Two or More Races",
                    "value": "Two or More Races"
                },
                {
                    "label": "Native Hawaiian or Other Pacific Islander",
                    "value": "Native Hawaiian or Other Pacific Islander",
                },
                {
                    "label": "White",
                    "value": "White",
                },
                {
                    "label": "Hispanic or Latino",
                    "value": "Hispanic or Latino",
                },
                {
                    "label": "Black or African American",
                    "value": "Black or African American",
                },
                {
                    "label": "Asian",
                    "value": "Asian"
                },
                {
                    "label": "American Indian or Alaskan Native",
                    "value": "American Indian or Alaskan Native"
                },
            ]
        },
        {
            "type": FieldType.SELECT,
            "title": "What is your military status?",
            "placeholder": "Choose military status",
            "order": 6,
            "items": [
                {
                    "label": "I don’t wish to answer",
                    "value": "I don’t wish to answer"
                },
                {
                    "label": "I identify as one or more of the classifications of a protected veteran",
                    "value": "I identify as one or more of the classifications of a protected veteran",
                },
                {
                    "label": "I am not a protected veteran",
                    "value": "I am not a protected veteran"
                },
            ],
        },
    ]

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        for q in self.ADDITIONAL_QUESTIONS:
            s, created = AdditionalQuestion.objects.update_or_create(title=q['title'], defaults=q)
        self.stdout.write('done.')

