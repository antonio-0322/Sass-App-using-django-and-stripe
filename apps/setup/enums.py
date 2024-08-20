from django.db import models


class FieldType(models.TextChoices):
    MULTI_INPUT = 'multi_input', 'Multi Input'
    INPUT = 'input', 'Input'
    NUMBER_INPUT = 'number_input', 'Number Input'
    SELECT = 'select', 'Select'
    RADIO = 'radio', 'Radio'
    CHECKBOX_GROUP = 'checkbox_group', 'Checkbox Group'
    MULTI_SELECT = 'multi_select', 'Multi Select'
    SWITCH_BUTTON = 'switch_button', 'Switch Button'


class FieldSlugs(models.TextChoices):
    JOB_TITLE = 'job_title', 'Job Title'
    SEARCH = 'search', 'Search'
    JOB_LOCATION = 'job_location', 'Job Location'
    JOB_TYPES = 'job_types', 'Job Types'
    EXCLUDED_COMPANIES = 'excluded_companies', 'Excluded Companies'
    ON_SITE_REMOTE = 'on_site_remote', 'On Site / Remote'
    EXPERIENCE_LEVEL = 'experience_level', 'Experience Level'
    EASY_APPLY = 'easy_apply', 'Easy Apply'
