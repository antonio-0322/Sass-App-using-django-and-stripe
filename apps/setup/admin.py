from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.
from apps.setup.models import AdditionalQuestion, JobSearchFilter

admin.site.register(AdditionalQuestion)
admin.site.register(JobSearchFilter)
