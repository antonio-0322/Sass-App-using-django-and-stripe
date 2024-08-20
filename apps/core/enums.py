from enum import Enum


class AbstractChoiceEnum(str, Enum):
    @classmethod
    def choices(cls):
        return [
            (member.value, name.capitalize())
            for name, member in cls.__members__.items()
        ]
