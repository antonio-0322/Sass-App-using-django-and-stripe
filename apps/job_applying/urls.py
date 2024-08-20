from django.urls import path

from apps.job_applying.views import *

urlpatterns = [
    path('verify-can-apply/<str:job_id>/<str:platform>', VerifyCanApplyToJobAPIView.as_view()),
    path('job-search-url/<str:platform>/', JobSearchUrlAPIView.as_view()),
    path('jobs/', AppliedJobsListAPIView.as_view()),
    path('create/', CreateAppliedJobAPIView.as_view()),
    path('get-pending-job/<str:job_id>/<str:platform>', GetPendingJobAPIView.as_view()),
    path('update/<int:pk>/', UpdateAppliedJob.as_view()),
    path('qa/<int:pk>', QAAPIView.as_view()),
    path('save-answer/', CreateAnswerAPIView.as_view()),
    path('resume-as-file/', DefaultResumeAsFileAPIView.as_view()),
]