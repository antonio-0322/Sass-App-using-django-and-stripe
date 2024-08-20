from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView

from apps.setup.models import AdditionalQuestion, JobSearchFilter
from apps.setup.serializers import AdditionalQuestionSerializer, JobSearchFilterSerializer


class AdditionalQuestionsListAPIView(ListAPIView):
    pagination_class = None
    serializer_class = AdditionalQuestionSerializer
    queryset = AdditionalQuestion.objects.all()


class JobSearchFiltersListAPIView(ListAPIView):
    serializer_class = JobSearchFilterSerializer
    queryset = JobSearchFilter.objects.all()

    def get_queryset(self):
        return JobSearchFilter.objects.filter(platform=self.kwargs.get('platform')).all()