from typing import Union

from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound, APIException
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class BaseValidationError(ValidationError):
    def __init__(self, detail: Union[str, list, dict] = None, error_code=None, code=None):
        if isinstance(detail, str):
            detail = {'detail': detail}
        if error_code:
            detail['error_code'] = error_code
        super().__init__(detail, code)


class BaseNotFoundError(NotFound):

    def __init__(self, detail: Union[str, list, dict] = None, code=None):
        if isinstance(detail, str):
            detail = {'detail': detail}

        super().__init__(detail, code)


class InActiveUser(AuthenticationFailed):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_detail = "Your account is not yet activated. Please check your email inbox " \
                     "and click on the activation link to get started."
    default_code = 'user_is_inactive'


class BaseAPIException(APIException):
    status_code = 400
    default_detail = 'Something went wrong.'
    default_code = 'error'


class LogicException(BaseAPIException):
    ...
