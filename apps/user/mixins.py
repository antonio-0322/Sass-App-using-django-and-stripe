import django.contrib.auth.password_validation as validators
import rest_framework
from django.core.exceptions import ValidationError
from rest_framework import serializers

from apps.core.exceptions import BaseValidationError
from apps.user.models import User
from apps.user.utils import verify_code


class RetrieveUserByEmailMixin:
    def get_object(self):
        if not self.request.data['email']:
            raise BaseValidationError({"email": "Email is required"})
        return User.objects.filter(email=self.request.data['email']).first()


class ValidatePasswordsMatchMixin:
    def validate(self, data):
        if not data.get('password'):
            raise BaseValidationError({"password": "Password is required"})
        if not data.get('password_confirm'):
            raise BaseValidationError({"password_confirm": "Password Confirm is required"})
        if data['password_confirm'] != data['password']:
            raise BaseValidationError({"password_confirm": "Passwords doesn't match"})

        return super().validate(data)


class ValidatePasswordRulesMixin:
    def validate(self, data):
        if not data.get('password'):
            raise BaseValidationError({"password": "Password is required"})

        """
            Validate that the password meets all validator requirements.

            If the password is valid, return ``None``.
            If the password is invalid, raise ValidationError with all error messages.
            """
        errors = []
        password_validators = validators.get_default_password_validators()
        for validator in password_validators:
            try:
                validator.validate(data['password'], User)
            except ValidationError as error:
                errors.append(error.message)
        if errors:
            raise BaseValidationError({"password": errors})

        return super().validate(data)


class ValidateCodeMixin:
    def validate(self, data):
        if not data.get('code'):
            raise BaseValidationError("Code is required")
        if not data.get('email'):
            raise BaseValidationError({"email": "Email is required"})

        verify_code(email=data.get('email'), code=data.get('code'))

        return super().validate(data)

