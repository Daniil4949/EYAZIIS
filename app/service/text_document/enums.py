from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return self.value


class Language(StrEnum):
    RUSSIAN = "ru"
    GERMAN = "de"
