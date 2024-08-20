from django.core.exceptions import ValidationError
from django.utils.translation import ngettext as _


class ContainsSpecialCharactersValidator:
    def __init__(self, min_characters=1):
        self.min_characters = min_characters
        self.characters = set(" !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")

    def validate(self, password, user=None):
        if sum(c in self.characters for c in password) < self.min_characters:
            raise ValidationError(
                _(f"Password must contain at least {self.min_characters} special character.",
                    f"Password must contain at least {self.min_characters} special characters.",
                    self.min_characters
                 ),
                code='password_too_weak',
                params={'min_characters': self.min_characters},
            )

    def get_help_text(self):
        return _(
            f"Your password must contain at least {self.min_characters} special character.",
            f"Your password must contain at least {self.min_characters} special characters.",
            self.min_characters
        )


class ContainsDigitsValidator:
    def __init__(self, min_digits=1):
        self.min_digits = min_digits

    def validate(self, password, user=None):
        if sum(c.isdigit() for c in password) < self.min_digits:
            raise ValidationError(
                _(
                    f"Password must contain at least {self.min_digits} number.",
                    f"Password must contain at least {self.min_digits} numbers.",
                    self.min_digits
                ),
                code='password_too_weak',
                params={'min_digits': self.min_digits},
            )

    def get_help_text(self):
        return _(
            f"Your password must contain at least {self.min_digits} number.",
            f"Your password must contain at least {self.min_digits} numbers.",
            self.min_digits
        )


class ContainsUppercaseValidator:
    def __init__(self, min_uppercase=1):
        self.min_uppercase = min_uppercase

    def validate(self, password, user=None):
        if sum(c.isupper() for c in password) < self.min_uppercase:
            raise ValidationError(
                _(
                    f"Password must contain at least {self.min_uppercase} uppercase letter.",
                    f"Password must contain at least {self.min_uppercase} uppercase letter.",
                    self.min_uppercase
                ),
                code='password_too_weak',
                params={'min_uppercase': self.min_uppercase},
            )

    def get_help_text(self):
        return _(
            f"Your password must contain at least {self.min_uppercase} uppercase character.",
            f"Your password must contain at least {self.min_uppercase} uppercase characters.",
            self.min_uppercase
        ) % {'min_uppercase': self.min_uppercase}


class ContainsLowercaseValidator:
    def __init__(self, min_lowercase=1):
        self.min_lowercase = min_lowercase

    def validate(self, password, user=None):
        if sum(c.islower() for c in password) < self.min_lowercase:
            raise ValidationError(
                _(
                    f"Password must contain at least {self.min_lowercase} lowercase letter.",
                    f"Password must contain at least {self.min_lowercase} lowercase letter.",
                    self.min_lowercase
                ),
                code='password_too_weak',
                params={'min_lowercase': self.min_lowercase},
            )

    def get_help_text(self):
        return _(
            f"Your password must contain at least {self.min_lowercase} lowercase letter.",
            f"Your password must contain at least {self.min_lowercase} lowercase letter.",
            self.min_lowercase
        )


class MinimumLengthValidator:
    """
    Validate that the password is of a minimum length.
    """

    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _(
                    f"Password must contain at least {self.min_length} character.",
                    f"Password must contain at least {self.min_length} characters.",
                    self.min_length,
                ),
                code="password_too_short",
                params={"min_length": self.min_length},
            )

    def get_help_text(self):
        return _(
            f"Password must contain at least {self.min_length} character.",
            f"Password must contain at least {self.min_length} characters.",
            self.min_length,
        )

