import functools

from rest_framework.exceptions import PermissionDenied

from apps.job_applying.exceptions import RequiresActiveSubscriptionException
from apps.job_applying.utils import validate_plan_limits


def active_plan_requires(view_func):
    @functools.wraps(view_func)
    def wrapped(self, request, *args, **kwargs):
        if not request.user.active_subscription:
            raise RequiresActiveSubscriptionException()
        return view_func(self, request, *args, **kwargs)
    return wrapped


def plan_limits_check_requires(view_func):
    @functools.wraps(view_func)
    def wrapped(self, request, *args, **kwargs):
        validate_plan_limits(request.user)
        return view_func(self, request, *args, **kwargs)
    return wrapped

