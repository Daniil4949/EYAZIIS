from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return self.value


class Mode(StrEnum):
    NEURAL = "neural"
    NGRAMM = "ngramm"
