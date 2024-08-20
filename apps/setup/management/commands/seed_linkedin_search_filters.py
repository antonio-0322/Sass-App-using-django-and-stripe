from django.core.management.base import BaseCommand

from apps.setup.enums import FieldType, FieldSlugs
from apps.setup.models import AdditionalQuestion, JobSearchFilter


class Command(BaseCommand):
    help = "seed Linkedin search filters"

    SEARCH_FILTERS = [
        {
            "type": FieldType.INPUT,
            "title": "Search",
            "slug": FieldSlugs.SEARCH,
            "is_required": True,
            "query_param": "keywords",
            "order": 1,
            "filter_name": "search",
            "element_xpath": "/html/body/div[5]/header/div/div/div/div[2]/div[1]/div/div/input[1]",
            "placeholder": "Enter title, skills, company"
        },
        {
            "type": FieldType.MULTI_INPUT,
            "title": "Job Title(s)",
            "is_required": True,
            "placeholder": "Choose Job Title(s)",
            "query_param": "f_T",
            "filter_name": "Title",
            "is_multiple": True,
            "order": 2,
            "can_be_added_in_search_url": False,
            "slug": FieldSlugs.JOB_TITLE
        },
        {
            "type": FieldType.INPUT,
            "title": "Job Location",
            "order": 3,
            "query_param": "location",
            "slug": FieldSlugs.JOB_LOCATION,
            "is_required": True,
            "filter_name": "location",
            "element_xpath": "/html/body/div[5]/header/div/div/div/div[2]/div[2]/div/div/input[1]",
            "placeholder": "Enter the location",
        },
        {
            "type": FieldType.MULTI_SELECT,
            "title": "Job Types",
            "placeholder": "Choose Job types",
            "query_param": "f_JT",
            "is_multiple": True,
            "slug": FieldSlugs.JOB_TYPES,
            "order": 4,
            "filter_name": "Job type",
            "items": [
                {
                    "label": "Full-time",
                    "value": "F"
                },
                {
                    "label": "Part-time",
                    "value": "P"
                },
                {
                    "label": "Contract",
                    "value": "C"
                },
                {
                    "label": "Volunteer",
                    "value": "V"
                },
                {
                    "label": "Temporary",
                    "value": "T"
                },
                {
                    "label": "Internship",
                    "value": "I"
                },
                {
                    "label": "Other",
                    "value": "O"
                }
            ]
        },
        {
            "type": FieldType.MULTI_INPUT,
            "title": "Excluded Companies",
            "filter_name": "excluded_companies",
            "order": 5,
            "slug": FieldSlugs.EXCLUDED_COMPANIES,
            "can_be_added_in_search_url": False,
            "is_multiple": True,
            "should_be_triggered_in_search_platform": False,
            "placeholder": "Choose Excluded companies",
        },
        {
            "type": FieldType.CHECKBOX_GROUP,
            "title": "On-site/remote",
            "query_param": "f_WT",
            "slug": FieldSlugs.ON_SITE_REMOTE,
            "order": 6,
            "is_multiple": True,
            "filter_name": "On-site/remote",
            "items": [
                {
                    "label": "On-site",
                    "value": "1"
                },
                {
                    "label": "Remote",
                    "value": "2"
                },
                {
                    "label": "Hybrid",
                    "value": "3"
                }
            ]
        },
        {
            "type": FieldType.MULTI_SELECT,
            "title": "Experience level",
            "placeholder": "Choose Experience Level",
            "query_param": "f_E",
            "slug": FieldSlugs.EXPERIENCE_LEVEL,
            "order": 7,
            "is_multiple": True,
            "filter_name": "Experience level",
            "items": [
                {
                    "label": "Internship",
                    "value": "1"
                },
                {
                    "label": "Entry level",
                    "value": "2"
                },
                {
                    "label": "Associate",
                    "value": "3"
                },
                {
                    "label": "Mid-Senior level",
                    "value": "4"
                },
                {
                    "label": "Director",
                    "value": "5"
                },
                {
                    "label": "Executive",
                    "value": "6"
                }
            ]
        },
        {
            "type": FieldType.SWITCH_BUTTON,
            "title": "Easy Apply",
            "filter_name": "Easy Apply",
            "query_param": "f_AL",
            "order": 8,
            "slug": FieldSlugs.EASY_APPLY,
            "fillable": False,
            "items": [
                {
                    "label": "Yes",
                    "value": True
                },
                {
                    "label": "No",
                    "value": False
                }
            ]
        },
    ]

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        for q in self.SEARCH_FILTERS:
            s, created = JobSearchFilter.objects.update_or_create(title=q['title'], defaults=q)
        self.stdout.write('done.')

