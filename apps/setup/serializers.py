from rest_framework import serializers

from apps.setup.models import AdditionalQuestion, JobSearchFilter


class AdditionalQuestionSerializer(serializers.ModelSerializer):
    items = serializers.ListSerializer(child=serializers.JSONField())

    class Meta:
        model = AdditionalQuestion
        fields = '__all__'


class JobSearchFilterSerializer(serializers.ModelSerializer):
    items = serializers.ListSerializer(child=serializers.JSONField())

    class Meta:
        model = JobSearchFilter
        fields = '__all__'
