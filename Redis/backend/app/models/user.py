from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Enum
from enums.gender import Gender
from config.database import meta

user = Table(
  'user', meta,
  Column('userID', Integer, primary_key=True, autoincrement=True),
  Column('name', String(255)),
  Column('age', Integer),  # Normally DoB is prefered - computed field
  Column('gender', Enum(Gender)),
  Column('email', String(255), unique=True, index=True)
)
