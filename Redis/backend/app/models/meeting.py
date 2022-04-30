from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Text, Boolean
from config.database import meta

meeting = Table(
  'meeting', meta,
  Column('meetingID', Integer, primary_key=True, autoincrement=True),
  Column('title', String(255)),
  Column('description', Text),
  Column('isPublic', Boolean)
)
