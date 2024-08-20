
from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampsModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(_('Last Update'), auto_now_add=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

