from django.db import models

# Create your models here.
from apps.core.models import TimestampsModel
from apps.job_applying.enums import JobStatuses, JobSearchPlatforms
from apps.payment.models import Subscription
from apps.user.models import User


class AppliedJob(TimestampsModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applied_jobs')
    title = models.CharField(max_length=125)
    job_url = models.URLField(max_length=800)
    used_subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='applied_jobs')
    job_id = models.CharField(max_length=40)
    platform = models.CharField(choices=JobSearchPlatforms.choices, max_length=25, default=JobSearchPlatforms.LINKEDIN)
    status = models.CharField(choices=JobStatuses.choices,  max_length=25, default=JobStatuses.CREATED)
    company = models.CharField(max_length=125, null=True)
    powered_by = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'applied_jobs'
        unique_together = ('job_id', 'user', 'platform')
        ordering = ('-created_at', )


class AppliedJobQA(TimestampsModel):
    job = models.ForeignKey(AppliedJob, on_delete=models.CASCADE, related_name='answers')
    question = models.TextField(null=True, blank=True)
    answer = models.TextField(null=True, blank=True)
    answer_options = models.JSONField(null=True, blank=True)
    prefilled_answer = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'applied_job_question_answers'
