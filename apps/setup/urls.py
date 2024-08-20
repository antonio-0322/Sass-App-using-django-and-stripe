from django.urls import path

from apps.setup.views import *

urlpatterns = [
    path('additional-questions/', AdditionalQuestionsListAPIView.as_view()),
    path('job-search-filters/<str:platform>/', JobSearchFiltersListAPIView.as_view())
]

