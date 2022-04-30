from enum import auto
from fastapi_utils.enums import StrEnum


class Gender(StrEnum):
  male = auto()
  female = auto()
