from rest_framework import serializers
from apps.job_applying.models import AppliedJob, AppliedJobQA


class AppliedJobQASerializer(serializers.ModelSerializer):

    class Meta:
        model = AppliedJobQA
        fields = '__all__'


class AppliedJobSerializer(serializers.ModelSerializer):
    answers = serializers.ListSerializer(child=AppliedJobQASerializer(), read_only=True)

    class Meta:
        model = AppliedJob
        fields = '__all__'
