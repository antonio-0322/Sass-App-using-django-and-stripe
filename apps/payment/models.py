from datetime import datetime

from django.core.files.storage import FileSystemStorage
from django.db import models

# Create your models here.
from apps.core.models import TimestampsModel
from apps.job_applying.enums import JobStatuses
from apps.user.models import User


class Plan(models.Model):
    class PlanSlugs(models.TextChoices):
        FREE = 'free', 'Free'
        BASIC = 'basic', 'Basic'
        PRO = 'pro', 'Pro',
        ADVANCED = 'advanced', 'Advanced'

    class Currencies(models.TextChoices):
        USD = 'usd', 'USD'

    class Interval(models.TextChoices):
        DAY = 'day', 'Day'
        WEEK = 'week', 'Week'
        MONTH = 'month', 'Month',
        YEAR = 'year', 'Year',

    name = models.CharField(max_length=35)
    slug = models.CharField(max_length=25, choices=PlanSlugs.choices, unique=True)
    label = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_length=8, max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, choices=Currencies.choices, default=Currencies.USD)
    description = models.TextField(max_length=500, null=True, blank=True)
    interval = models.CharField(max_length=10, choices=Interval.choices, default=Interval.MONTH)
    stripe_price_id = models.CharField(max_length=30, null=True, blank=True)
    active = models.BooleanField(default=True)
    image = models.CharField(null=True, blank=True, max_length=50)
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'plans'

    @property
    def is_chargeable(self):
        return self.amount > 0

    @property
    def job_applications_per_day(self):
        option = self.options.filter(type=PlanOption.PlanOptionTypes.JOB_APPLICATIONS_PER_DAY).first()
        return option.value if option else 0


class PlanOption(models.Model):
    class PlanOptionTypes(models.TextChoices):
        RESUMES_COUNT = 'resumes_count', 'Resume'
        JOB_TITLE = 'job_title', 'Job title'
        JOB_APPLICATIONS = 'job_applications', 'Job applications'
        FREE_ACCESS = 'free_access', 'Free Access'
        JOB_APPLICATIONS_TRACKER = 'submission_tracker', 'Job submission tracker'
        FILTER_OUT_COMPANIES = 'filter_companies', 'Filter out companies'
        JOB_APPLICATIONS_PER_DAY = 'job_applies_per_day', 'Job applies per day'
    text = models.CharField(max_length=300)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='options')
    type = models.CharField(choices=PlanOptionTypes.choices, max_length=30)
    value = models.PositiveIntegerField(null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.text

    class Meta:
        db_table = 'plan_options'


class Subscription(TimestampsModel):
    plan = models.ForeignKey(Plan, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='subscriptions')
    end_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
    stripe_webhook_id = models.CharField(max_length=50, null=True, blank=True)
    stripe_webhook_created_at = models.DateTimeField(auto_now_add=False, null=True)

    @property
    def used_jobs_submissions(self):
        return self.applied_jobs.filter(status=JobStatuses.APPLIED).count()

    @property
    def total_job_submissions(self):
        option = self.plan.options.filter(type=PlanOption.PlanOptionTypes.JOB_APPLICATIONS).first()
        return option.value if option else 0

    @property
    def possible_job_submissions(self):
        val = self.total_job_submissions - self.used_jobs_submissions
        return val if val > 0 else 0

    @property
    def possible_job_titles(self):
        val = self.total_job_titles - self.used_job_titles
        return val if val > 0 else 0

    @property
    def total_job_titles(self):
        option = self.plan.options.filter(type=PlanOption.PlanOptionTypes.JOB_TITLE).first()
        return option.value if option else 0

    @property
    def used_job_titles(self):
        return self.user.job_titles.filter(is_active=True).count()

    @property
    def today_used_applications(self):
        return self.applied_jobs.filter(
            created_at__gte=datetime.now().date(),
            status=JobStatuses.APPLIED,
            used_subscription_id=self.id
        ).count()

    @property
    def daily_job_applications(self):
        return self.plan.job_applications_per_day

    class Meta:
        db_table = 'subscriptions'
