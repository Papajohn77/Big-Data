from sqlalchemy import Table, Column
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, DateTime, Enum
from enums.event_type import EventType
from config.database import meta

event_log = Table(
  'event_log', meta,
  Column('eventID', Integer, primary_key=True, autoincrement=True),
  Column('userID', Integer, ForeignKey('user.userID')),
  Column('eventType', Enum(EventType)),
  Column('timestamp', DateTime(timezone=True), server_default=func.now())
)
