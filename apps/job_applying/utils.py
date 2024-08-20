import datetime

from typing import Union
from django.conf import settings
from django.utils import timezone

from apps.core.exceptions import BaseValidationError, BaseNotFoundError
from apps.job_applying.enums import JobSearchPlatforms, LinkedinPoweredByChoices, JobStatuses
from apps.job_applying.exceptions import PlanLimitExceededException, RequiresActiveSubscriptionException, \
    JobSubmissionsDelayException, DuplicateApplyException, ApplyingToExcludedCompanyJobException
from apps.job_applying.models import AppliedJob, AppliedJobQA
from apps.user.models import User, UserJobSearchFilter


def verify_user_can_apply_to_job(
        user: User,
        job_id: str,
        powered_by: str,
        company: str,
        platform: JobSearchPlatforms = JobSearchPlatforms.LINKEDIN,
) -> None:
    """
       Verifies if a user can apply for a job based on the provided parameters.
       Args:
           user (User): The user attempting to apply for the job.
           job_id: The ID of the job being applied for.
           platform (str, optional): The platform from which the user is applying. Defaults is 'Linkedin'.
           powered_by (str): If platform is LinkedIn job should be powered by particular companies.
           company (str):
       Raises:
           DuplicateApplyException: If the user has applied for that job already or he has applied job with status created.
       Returns:
           None
   """
    if company:
        validate_company(company=company, user=user)

    job = AppliedJob.objects.filter(
        user=user,
        job_id=job_id,
        platform=platform,
        status__in=[JobStatuses.APPLIED, JobStatuses.FAILED]
    ).exists()

    if job:
        raise DuplicateApplyException()

    if platform == JobSearchPlatforms.LINKEDIN.value:
        validate_powered_by(powered_by)

    validate_job_submission_delay(user)


def validate_plan_limits(user: User) -> None:
    """
        Validates the usage limits of a user's subscription plan for job submissions.

        This function checks whether the user's subscription plan allows for job submissions,
        taking into account the user's active subscription status and the limits set by the plan.
        If any of the validation checks fail, specific exceptions are raised to indicate the issue.
        Args:
            user (User): The user for whom the subscription plan limits need to be validated.
        Raises:
            RequiresActiveSubscriptionException: If the user does not have an active subscription.
            PlanLimitExceededException: If the user has exceeded either the overall job submissions
                limit for the plan or the daily job submissions limit for the plan.

        """
    if not user.active_subscription:
        raise RequiresActiveSubscriptionException()

    if user.active_subscription.possible_job_submissions <= 0:
        raise PlanLimitExceededException("You already have exceeded job submissions limit for this plan")

    if user.active_subscription.today_used_applications >= user.active_subscription.daily_job_applications:
        raise PlanLimitExceededException("You already have exceeded daily job submissions limit for this plan")


def validate_powered_by(powered_by: str):
    """
        Validates whether the provided 'powered_by' value is valid for LinkedIn jobs.
        This function checks if the given 'powered_by' value matches any of the predefined choices
        for powering a LinkedIn job application. If the provided value is not one of the valid choices,
        a BaseValidationError is raised.

        Args:
            powered_by (str): The value representing the platform used to power the job application.
        Raises:
            BaseValidationError: Raised when the provided 'powered_by' value is not a valid choice for
                powering a LinkedIn job application.
        """
    if not powered_by or not powered_by.lower() in [v.lower() for v in LinkedinPoweredByChoices.values]:
        raise BaseValidationError(
            f"Application should be powered by {LinkedinPoweredByChoices.values} for Linkedin jobs"
        )


def validate_job_submission_delay(user: User) -> None:
    """
    This function validates whether a user is allowed to submit a job application based on a specified delay interval.
    If a recent job submission is found, the function raises a ``JobSubmissionsDelayException``
       to prevent further job submissions within the specified interval.
   :param user: The user for whom the job submission delay is being validated.
   :type user: User
   :raises JobSubmissionsDelayException:If the user has submitted a job application within the configured delay interval.
    """
    j = AppliedJob.objects.filter(
        user=user,
        created_at__gte=timezone.now() - datetime.timedelta(seconds=settings.JOB_APPLYING_INTERVAL)
    ).exists()

    if j:
        raise JobSubmissionsDelayException()


def validate_company(company: str, user: User):
    """
        Validates whether the provided company is excluded based on the user's job search filters.
        This function checks if the given company is present in the list of excluded companies
        specified in the user's job search filters. If the company is found in the exclusion list,
        an ApplyingToExcludedCompanyJobException is raised.
        Args:
            company (str): The name of the company to be validated.
            user (User): The user for whom the company validation is being performed.
        Raises:
            ApplyingToExcludedCompanyJobException: Raised when the provided company is found in the
                list of excluded companies in the user's job search filters.
        """
    excluded_companies = user.job_search_filters.filter(job_search_filter__filter_name='excluded_companies').first()

    if excluded_companies and company.lower() in [c.lower() for c in excluded_companies.values]:
        raise ApplyingToExcludedCompanyJobException()


def save_answer(job: AppliedJob, question: str, answer: str, answer_options: list = None, prefilled_answer: str = None):
    AppliedJobQA.objects.create(
        answer=answer,
        job=job,
        question=question,
        answer_options=answer_options,
        prefilled_answer=prefilled_answer
    )


def user_job_titles(user: User, platform: JobSearchPlatforms= JobSearchPlatforms.LINKEDIN) -> list:
    job_search_filter = UserJobSearchFilter.objects.filter(
        job_search_filter__platform=platform,
        user=user,
        job_search_filter__slug='job_title').first()

    return job_search_filter.values if job_search_filter else []


def get_pending_job(
        user: User,
        job_id: str,
        platform: JobSearchPlatforms = JobSearchPlatforms.LINKEDIN
) -> Union[None, AppliedJob]:
    """
    Returns pending job if exists otherwise None
    """
    return AppliedJob.objects.filter(
        user=user,
        status=JobStatuses.CREATED,
        job_id=job_id,
        platform=platform
    ).first()
