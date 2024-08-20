from django.db import models

# Create your models here.
from apps.core.models import TimestampsModel
from apps.job_applying.enums import JobSearchPlatforms
from apps.setup.enums import FieldType


class Field(models.Model):
    type = models.CharField(choices=FieldType.choices, max_length=25)
    title = models.CharField(max_length=300, null=True, blank=True)
    is_required = models.BooleanField(default=False)
    placeholder = models.CharField(max_length=45, null=True)
    hint = models.CharField(max_length=300, null=True, blank=True)
    description = models.CharField(max_length=400, null=True, blank=True)
    data_attrs = models.JSONField(null=True, blank=True)
    items = models.JSONField(null=True)
    slug = models.CharField(null=True, blank=True, max_length=25)

    class Meta:
        abstract = True


class AdditionalQuestion(Field, TimestampsModel):
    order = models.IntegerField(null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'additional_questions'
        ordering = ('order',)


class JobSearchFilter(Field, TimestampsModel):
    platform = models.CharField(max_length=20, default=JobSearchPlatforms.LINKEDIN)
    filter_name = models.CharField(max_length=45)
    element_xpath = models.CharField(max_length=300, null=True, blank=True)
    query_param = models.CharField(max_length=45, null=True, blank=True)
    can_be_added_in_search_url = models.BooleanField(default=True)
    should_be_triggered_in_search_platform = models.BooleanField(default=True)
    fillable = models.BooleanField(default=True)
    order = models.PositiveIntegerField(null=True)
    is_multiple = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'job_search_filters'
        ordering = ('order', )
