from django.contrib import admin

# Register your models here.
from apps.payment.models import Plan, PlanOption

admin.site.register(Plan)

admin.site.register(PlanOption)