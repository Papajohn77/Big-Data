from enum import auto
from fastapi_utils.enums import StrEnum


class EventType(StrEnum):
  join = auto()
  leave = auto()
