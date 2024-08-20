import base64
import uuid
import six
import filetype


from django.core.files.base import ContentFile
from rest_framework import serializers
from django.core.files.storage import default_storage

from apps.core.exceptions import BaseValidationError


class Base64StringField(serializers.FileField):
    def __init__(self, max_size=None, min_size=None, allowed_extensions = None, **kwargs):
        self.max_size = max_size
        self.min_size = min_size
        self.allowed_extensions = allowed_extensions
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if self.__validate_base64_string(data):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')
            decoded_file = self.__decode_file(data)
            file_extension = self.__get_file_extension(decoded_file)
            if self.allowed_extensions and file_extension not in self.allowed_extensions:
                raise BaseValidationError(f"Allowed Extensions are {self.allowed_extensions}")
            if not decoded_file:
                filepath = '/'.join(data.split("/")[-2:])
                if not default_storage.exists(filepath):
                    raise BaseValidationError("Wrong file provided.")
                return filepath
            else:
                file_extension = self.__get_file_extension(decoded_file)
                file_name = str(uuid.uuid4())
                complete_file_name = "%s.%s" % (file_name, file_extension)
                data = ContentFile(decoded_file, name=complete_file_name)

        return super().to_internal_value(data)

    def __validate_base64_string(self, data: str):
        if not isinstance(data, six.string_types):
            raise BaseValidationError('Invalid base64 string')

        file_size = len(data) * 3/4  # in bytes
        if self.min_size and file_size < self.min_size * 1000:
            raise BaseValidationError(f'The file must be larger than {self.min_size} KB')

        if self.max_size and file_size > self.max_size * 1000:
            raise BaseValidationError(f'The file must be no larger than {self.max_size} KB')

        return True

    @staticmethod
    def __get_file_extension(file):
        return filetype.guess_extension(file)

    @staticmethod
    def __decode_file(data):
        try:
            return base64.b64decode(data)
        except:
            return False
