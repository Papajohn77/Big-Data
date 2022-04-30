from typing import Optional
from pydantic import BaseModel


class Message(BaseModel):
  userID: int
  body: str
