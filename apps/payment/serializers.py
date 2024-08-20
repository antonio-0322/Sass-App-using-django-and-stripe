import os

from django.conf import settings
from rest_framework import serializers

from apps.payment.models import Plan, PlanOption, Subscription

from urllib.parse import urljoin

class PlanOptionSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')

    class Meta:
        model = PlanOption
        exclude = ('plan', )


class PlanSerializer(serializers.ModelSerializer):
    interval = serializers.CharField(source='get_interval_display')
    currency = serializers.CharField(source='get_currency_display')
    options = PlanOptionSerializer(many=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = '__all__'

    def get_image(self, obj):
        return urljoin(settings.BASE_URL, os.path.join(settings.STATIC_URL, obj.image))


class SubscriptionSerializer(serializers.ModelSerializer):
    job_submissions = serializers.SerializerMethodField()
    job_titles = serializers.SerializerMethodField()
    today_applications = serializers.SerializerMethodField()
    # plan = PlanSerializer()

    @staticmethod
    def get_job_submissions(obj):
        return {
            "used": obj.used_jobs_submissions,
            "total": obj.total_job_submissions,
            "possible": obj.possible_job_submissions
        }

    @staticmethod
    def get_job_titles(obj):
        return {
            "used": obj.used_job_titles,
            "total": obj.total_job_titles,
            "possible": obj.possible_job_titles
        }

    @staticmethod
    def get_today_applications(obj):
        u = obj.today_used_applications
        t = obj.daily_job_applications
        p = t - u
        return {
            "used": u,
            "total": t,
            "possible": p if p > 0 else 0
        }

    class Meta:
        model = Subscription
        fields = (
            'id',
            'created_at',
            'end_date',
            'active',
            'plan',
            'job_submissions',
            'job_titles',
            'today_applications'
        )
