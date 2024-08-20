import functools
import json
import logging

from apps.core.exceptions import BaseValidationError


def validate_request_params(serializer_class):
    def wrapper(view_func):
        @functools.wraps(view_func)
        def wrapped(self, request, *args, **kwargs):
            data = {key: value for key, value in request.query_params.items()}
            data.update(kwargs)
            data.update(request.data)
            validation = serializer_class(data=data)
            if not validation.is_valid():
                raise BaseValidationError(validation.errors)
            return view_func(self, request, *args, **kwargs)
        return wrapped
    return wrapper


def request_logger(logger):
    def wrapper(view_func):
        @functools.wraps(view_func)
        def wrapped(self, request, *args, **kwargs):
            data = {
                "query_params": {key: value for key, value in request.query_params.items()},
                "kwargs": kwargs,
                "data": request.data,
                "user": request.user.id
            }

            try:
                logger.debug(
                    f"Log Request, action: {view_func.__module__}.{view_func.__qualname__}"
                    f"\n {json.dumps(data, indent=4)}",
                )
            except:
                pass

            return view_func(self, request, *args, **kwargs)
        return wrapped
    return wrapper
