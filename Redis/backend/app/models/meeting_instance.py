from sqlalchemy import Table, Column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Integer, DateTime
from config.database import meta

meeting_instance = Table(
  'meeting_instance', meta,
  Column('meetingID', Integer, ForeignKey('meeting.meetingID'), primary_key=True),
  Column('orderID', Integer, primary_key=True),
  Column('fromdatetime', DateTime(timezone=True)),
  Column('todatetime', DateTime(timezone=True))
)
