from django.conf import settings

from apps.core.exceptions import BaseAPIException


class PlanLimitExceededException(BaseAPIException):
    default_detail = 'Plan limit exceeded'
    default_code = 'limit_exceeded'
    status_code = 423


class RequiresActiveSubscriptionException(BaseAPIException):
    default_detail = 'Requires active subscription'
    default_code = 'active_subscription_requires'
    status_code = 423


class JobSubmissionsDelayException(BaseAPIException):
    default_detail = f'Frequently job submissions error'
    default_code = 'job_submissions_delay_error'
    status_code = 429


class DuplicateApplyException(BaseAPIException):
    default_detail = f'This job has already been tried for apply.'
    default_code = 'duplicate_apply_Exception'


class OpenAIRateLimitException(BaseAPIException):
    default_detail = "Rate limit exceeded please try again later"
    default_code = "open_ai_rate_limit_error"
    status_code = 429


class ApplyingToExcludedCompanyJobException(BaseAPIException):
    default_detail = "Applying to excluded company's job."
    default_code = "applying_excluded_company_job"


class AlreadyExistsPendingJobException(BaseAPIException):
    default_detail = "This job already exists with status CREATED"
    default_code = "already_exists_pending_job"
    status_code = 409
