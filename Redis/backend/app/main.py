import logging
import datetime
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from routers.function import function
from enums.event_type import EventType
from sqlalchemy import text
from config.cache import cache
from config.database import engine, meta
from models import user, event_log, meeting,  meeting_instance, audience


meta.create_all()  # Create DB tables if not exist


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s')
handler = logging.FileHandler('../logs/errors.txt')
handler.setFormatter(formatter)

exception_logger = logging.getLogger(__name__)
exception_logger.addHandler(handler)


app = FastAPI()
app.include_router(function)


@app.on_event("startup")
def load_users():
  try:
    with engine.connect() as conn:
      users = conn.execute(text("SELECT * FROM user"))

      for userID, name, age, gender, email in users:
        cache.hmset(f'user:{userID}', {
          "name": name,
          "age": age,
          "gender": gender,
          "email": email
        })
  except Exception as exc:
    exception_logger.exception(exc)


def delete_logs(meeting_instance_key: str):
  with engine.connect() as conn:
    logs = cache.lrange(f'{meeting_instance_key}:logs', 0, -1)
    for eventID in logs:
      userID, eventType, timestamp = \
        cache.hmget(f'log:{eventID}', ["userID", "eventType", "timestamp"])

      conn.execute(text(f"""
        INSERT INTO event_log (userID, eventType, timestamp)
        VALUES ({userID}, "{eventType}", "{timestamp}")
      """))

      cache.delete(f'log:{eventID}')
    cache.delete(f'{meeting_instance_key}:logs')


def delete_participants(meeting_instance_key: str, finish_time: str):
  with engine.connect() as conn:
    participants = cache.lrange(f'{meeting_instance_key}:participants', 0, -1)
    for userID in participants:
      conn.execute(text(f"""
        INSERT INTO event_log (userID, eventType, timestamp)
        VALUES ({userID}, '{EventType.leave}', '{finish_time}')
      """))
    cache.delete(f'{meeting_instance_key}:participants')


def delete_messages(meeting_instance_key: str):
  with engine.connect() as conn:
    messages = cache.lrange(f'{meeting_instance_key}:messages', 0, -1)
    for messageID in messages:
      cache.delete(f'message:{messageID}')
    cache.delete(f'{meeting_instance_key}:messages')


def create_audience(meeting_instance_key: str, meetingID: int):
  with engine.connect() as conn:
    audience = conn.execute(text(f"""
      SELECT email
      FROM meeting as m, audience as a
      WHERE m.meetingID = {meetingID}
      AND m.meetingID = a.meetingID
    """))

    for email, in audience:
      cache.rpush(f'{meeting_instance_key}:audience', email)


@app.on_event("startup")
@repeat_every(seconds=15)
def activate_meetings():
  try:
    current_time = datetime.datetime.now()

    with engine.connect() as conn:
      meetings = conn.execute(text("""
        SELECT m.meetingID, orderID, title, description, isPublic, fromdatetime, todatetime
        FROM meeting as m, meeting_instance as mi
        WHERE m.meetingID = mi.meetingID
      """))

    for meetingID, orderID, title, description, isPublic, start_time, finish_time in meetings:
      meeting_instance_key = f'meeting:{meetingID}:order:{orderID}'

      if cache.sismember('active_meetings', meeting_instance_key):
        if current_time > finish_time:
          cache.srem('active_meetings', meeting_instance_key)
          cache.delete(meeting_instance_key)
          cache.delete(f'{meeting_instance_key}:audience')
          delete_logs(meeting_instance_key)
          delete_participants(meeting_instance_key, str(finish_time))
          delete_messages(meeting_instance_key)
      else:
        if start_time < current_time < finish_time:
          cache.sadd('active_meetings', meeting_instance_key)
          cache.hmset(meeting_instance_key, {
            "title": title,
            "description": description,
            "isPublic": isPublic,
            "fromdatetime": str(start_time),
            "todatetime": str(finish_time)
          })

          if not(isPublic):
            create_audience(meeting_instance_key, meetingID)
  except Exception as exc:
    exception_logger.exception(exc)
