import logging
import urllib

# Create your views here.
import openai
from django.http import HttpResponse, FileResponse
from django.utils.decorators import method_decorator
from rest_framework import status, filters
from django_filters import rest_framework as filters
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.decorators import request_logger
from apps.core.exceptions import BaseValidationError, BaseAPIException
from apps.core.pagination import DynamicPageSizePagination
from apps.job_applying.decorators import active_plan_requires, plan_limits_check_requires
from apps.job_applying.enums import JobSearchPlatforms
from apps.job_applying.exceptions import OpenAIRateLimitException, AlreadyExistsPendingJobException
from apps.job_applying.filters import AppliedJobFilter
from apps.job_applying.models import AppliedJob
from apps.job_applying.serializers import AppliedJobSerializer, AppliedJobQASerializer
from apps.job_applying.services.job_searching import job_search_builder_factory
from apps.job_applying.services.openai import QAService
from apps.job_applying.utils import verify_user_can_apply_to_job, save_answer, user_job_titles, get_pending_job
from apps.payment.utils import set_subscription_expired

logger = logging.getLogger('job_applying')


class AppliedJobsListAPIView(ListAPIView):
    serializer_class = AppliedJobSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = AppliedJobFilter
    pagination_class = DynamicPageSizePagination
    search_fields = [
        'title',
    ]

    def get_queryset(self):
        return AppliedJob.objects.filter(user=self.request.user).all()

    ordering_fields = ['id', 'title', 'company', 'status', 'company', 'created_at']


class CreateAppliedJobAPIView(CreateAPIView):
    serializer_class = AppliedJobSerializer

    @request_logger(logger=logging.getLogger('job_applying'))
    @active_plan_requires
    @plan_limits_check_requires
    def post(self, request, *args, **kwargs):
        verify_user_can_apply_to_job(
            user=request.user,
            job_id=request.data['job_id'],
            powered_by=request.data.get('powered_by'),
            company=request.data.get('company')
        )
        serializer = self.serializer_class(data={
            **request.data,
            "user": request.user.id,
            "used_subscription": request.user.active_subscription.id
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class VerifyCanApplyToJobAPIView(APIView):
    """
        API view to verify if a user can apply for a job based on their subscription plan limits.

        This view checks whether the user's subscription plan allows for job applications,
        and whether the user has reached their daily application limits.

        Note:
            This view applies the decorators `active_plan_requires` and `plan_limits_check_requires`
            to ensure that the user has an active subscription and meets the job submission limits.
        Args:
            APIView (class): Django Rest Framework's APIView class.
        Raises:
            RequiresActiveSubscriptionException: If the user does not have an active subscription.
            PlanLimitExceededException: If the user has exceeded either the overall job submissions
                limit for the plan or the daily job submissions limit for the plan.
        """

    @request_logger(logger=logging.getLogger('job_applying'))
    @active_plan_requires
    @plan_limits_check_requires
    def get(self, request, job_id: str, platform: JobSearchPlatforms):
        """
           Verifies if the user can apply for a job based on the provided parameters.
           Args:
               request: Django request object.
               job_id (str): The ID of the job being applied for.
               platform (JobSearchPlatforms): The platform from which the user is applying.
           Returns:
               Response: Django Response object indicating the result of the verification.
               Returns status HTTP_200_OK if the user can apply, else raises exceptions.

        """
        powered_by = request.query_params.get('powered_by')
        company = request.query_params.get('company')
        verify_user_can_apply_to_job(
            user=request.user,
            job_id=job_id,
            platform=platform,
            powered_by=powered_by,
            company=company
        )

        # check if user has created that job already , which remained in progress
        if get_pending_job(user=request.user, job_id=job_id, platform=platform):
            raise AlreadyExistsPendingJobException()

        return Response(status=status.HTTP_200_OK)


class GetPendingJobAPIView(APIView):
    def get(self, request, job_id, platform):
        pending_order = get_pending_job(request.user, job_id, platform)
        if not pending_order:
            raise NotFound()
        serializer = AppliedJobSerializer(pending_order)

        return Response(serializer.data)


class CreateAnswerAPIView(APIView):
    serializer_class = AppliedJobQASerializer

    @request_logger(logger=logging.getLogger('job_applying'))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class QAAPIView(RetrieveAPIView):
    queryset = AppliedJob.objects.all()

    @request_logger(logger=logging.getLogger('job_applying'))
    @active_plan_requires
    @plan_limits_check_requires
    def get(self, request, **kwargs):

        if not request.query_params.get('question'):
            raise BaseValidationError("Question is required parameter")
        try:
            job = self.get_object()
            answer = QAService(user=request.user).get_answer(
                question=urllib.parse.unquote(request.query_params.get('question')),
                answer_options=request.query_params.getlist('answer_options'),
                output_type=request.query_params.get('output_type'),
            )
            save_answer(
                job=job,
                question=request.query_params.get('question'),
                answer=answer,
                answer_options=request.query_params.getlist('answer_options'),
                prefilled_answer=request.query_params.get('prefilled_answer')
            )
        except OpenAIRateLimitException: #TODO handle specific exceptions
            raise OpenAIRateLimitException()
        except Exception as e:
            logger.error(f"Failed QA: {str(e)}")
            raise BaseAPIException(str(e))
        return Response({"answer": answer}, status=200)


class JobSearchUrlAPIView(APIView):
    """
        A view for generating job search URLs based on the specified platform and user.
        This APIView takes a platform and user information to create a job search URL using a builder
        generated by the `job_search_builder_factory` function. The resulting URL can be used to perform
        job searches on various platforms.

        Parameters:
            - platform (str): The platform for which the job search URL is to be generated.
            - request (HttpRequest): The HTTP request object.
            - *args: Variable length argument list.
            - **kwargs: Arbitrary keyword arguments.

        Returns:
            A Response object containing the generated job search URL.
        """

    @active_plan_requires
    @plan_limits_check_requires
    def get(self, request, platform, *args, **kwargs):
        builder = job_search_builder_factory(platform, request.user)
        url = builder.build_search_url()

        return Response({"url": url, "job_titles": user_job_titles(user=request.user, platform=platform)})


class DefaultResumeAsFileAPIView(APIView):
    @active_plan_requires
    @plan_limits_check_requires
    def get(self, request, *args, **kwargs):
        """
            Handle GET request to download the user's selected resume.
            Args:
                request (HttpRequest): The HTTP request object.
                *args: Variable-length argument list.
                **kwargs: Keyword arguments.
            Returns:
                FileResponse: A file response containing the user's selected resume file.
        """
        resume = request.user.selected_resume

        if not resume or not resume.file.file:
            raise BaseValidationError("User doesn't have selected resume")

        response = FileResponse(resume.file.file)
        response['Content-Disposition'] = f'attachment; filename="{resume.file.name}"'
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'

        return response


class UpdateAppliedJob(UpdateAPIView):
    serializer_class = AppliedJobSerializer

    def get_queryset(self):
        return AppliedJob.objects.filter(user=self.request.user).all()

    def update(self, request, *args, **kwargs):
        res = super(UpdateAppliedJob, self).update(request, *args, **kwargs)
        if request.user.active_subscription.possible_job_submissions <= 0:
            set_subscription_expired(request.user.active_subscription)

        return res
