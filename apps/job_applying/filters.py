from django_filters import rest_framework as filters

from apps.job_applying.models import AppliedJob


class AppliedJobFilter(filters.FilterSet):
    class Meta:
        model = AppliedJob
        fields = {
            'title': ['icontains'],
            'created_at': ['lte', 'gte'],
            'status': ['exact'],
            'company': ['icontains'],
        }
