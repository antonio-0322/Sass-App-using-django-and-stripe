import datetime
import os

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q
from django.dispatch import receiver

from apps.core.models import TimestampsModel
from django.utils.translation import gettext_lazy as _

from apps.setup.models import AdditionalQuestion, JobSearchFilter
from apps.user.enums import SignupTypes
from apps.user.managers import UserManager


class User(AbstractUser, TimestampsModel):
    username = None
    email = models.EmailField(
        _("Email"),
        blank=False,
        null=False,
        unique=True,
        error_messages={'unique': "This email address is already registered."}
    )
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
    first_name = models.CharField(blank=True, null=True, max_length=25)
    last_name = models.CharField(blank=True, null=True, max_length=25)
    stripe_customer_id = models.CharField(max_length=50, null=True, blank=True)
    objects = UserManager()
    selected_resume = models.ForeignKey(
        'user.UserResume',
        on_delete=models.SET_NULL,
        null=True, related_name='selected_resume'
    )

    signup_type = models.CharField(choices=SignupTypes.choices, default=SignupTypes.EMAIL, max_length=20)
    is_welcome_said = models.BooleanField(default=False)

    class Meta:
        db_table = 'auth_user'

    @property
    def active_subscription(self):
        return self.subscriptions.filter(active=True).filter(
            Q(plan__amount__gt=0) | Q(end_date__gte=datetime.datetime.now().date())
        ).first()

    @property
    def has_used_free_subscription(self):
        return self.subscriptions.filter(plan__amount=0).exists()

    @property
    def last_used_subscription(self):
        return self.subscriptions.order_by('-created_at').filter(
            Q(stripe_webhook_id__isnull=True, plan__amount=0) |
            Q(stripe_webhook_id__isnull=False)
        ).first()


class UserEmailVerificationCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=45)
    expires_in = models.DateTimeField()

    class Meta:
        db_table = "user_verification_codes"


class UserJobTitle(TimestampsModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_titles')
    job_title = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_job_titles'


class UserResume(TimestampsModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])]
    )
    display_name = models.CharField(max_length=155)

    class Meta:
        db_table = 'user_resumes'

    @property
    def extension(self):
        parts = os.path.splitext(self.file.name)
        return parts[-1]

    @property
    def is_pdf(self):
        return self.extension == '.pdf'

    @property
    def is_docx(self):
        return self.extension == '.docx'


class UserSkill(TimestampsModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=35)
    experience_in_years = models.PositiveIntegerField()

    class Meta:
        db_table = 'user_skills'


class UserAdditionalQuestion(TimestampsModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='additional_questions')
    additional_question = models.ForeignKey(AdditionalQuestion, on_delete=models.CASCADE)
    value = models.CharField(max_length=300, null=True, blank=True)
    is_multiple = models.BooleanField(default=False)
    values = models.JSONField(null=True)
    metadata = models.JSONField(null=True)

    class Meta:
        db_table = 'user_additional_questions'


class UserJobSearchFilter(TimestampsModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_search_filters')
    job_search_filter = models.ForeignKey(JobSearchFilter, on_delete=models.CASCADE)
    value = models.CharField(max_length=300, null=True, blank=True)
    is_multiple = models.BooleanField(default=False)
    values = models.JSONField(null=True)
    metadata = models.JSONField(null=True)

    class Meta:
        db_table = 'user_job_search_filters'

class UserResumeParsed(TimestampsModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_resume_parsed')
    data = models.JSONField(null=True)

    class Meta:
        db_table = 'user_resume_parsed'

@receiver(models.signals.post_delete, sender=UserResume)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.file.delete(save=False)
