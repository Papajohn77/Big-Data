from sqlalchemy import Table, Column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from config.database import meta


audience = Table(
  'audience', meta,
  Column('meetingID', Integer, ForeignKey('meeting.meetingID'), primary_key=True),
  Column('email', String(255), ForeignKey('user.email'), primary_key=True)
)
