from django.db import models


class JobStatuses(models.TextChoices):
    CREATED = 'created', 'Created'
    APPLIED = 'applied', 'Applied'
    FAILED = 'failed', 'Failed'
    CANCELED = 'canceled', 'Canceled'


class JobSearchPlatforms(models.TextChoices):
    LINKEDIN = 'linkedin', 'LinkedIn'


class LinkedinPoweredByChoices(models.TextChoices):
    LINKEDIN = 'Linkedin', 'Linkedin'
    GREENHOUSE = 'Greenhouse', 'Greenhouse'
    LEVER = 'Lever', 'Lever'
