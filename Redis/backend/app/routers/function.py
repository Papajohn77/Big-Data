import logging
import datetime
from typing import List, Dict, Union
from fastapi import APIRouter, HTTPException
from schemas.message import Message
from enums.event_type import EventType
from config.cache import cache
from config.database import engine


function = APIRouter(
  tags=['Functions']
)


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s')
handler = logging.FileHandler('../logs/errors.txt')
handler.setFormatter(formatter)

exception_logger = logging.getLogger(__name__)
exception_logger.addHandler(handler)


class MeetingNotExistOrInactive(Exception):
  pass


class UserForbiddenToJoinMeeting(Exception):
  pass


class UserAlreadyInMeeting(Exception):
  pass


class UserNotInMeeting(Exception):
  pass


def check_if_meeting_exists(meeting_instance_key: str):
  exists = cache.exists(meeting_instance_key)
  if not(exists):
    raise MeetingNotExistOrInactive(
      'This meeting either does not exist or it is inactive.')


def check_if_user_already_in_meeting(meeting_instance_key: str, userID: int):
  participants = cache.lrange(f'{meeting_instance_key}:participants', 0, -1)
  if str(userID) in participants:
    raise UserAlreadyInMeeting('You have already joined in the meeting!')


def check_if_user_forbidden_to_join_meeting(meeting_instance_key: str, userID: int):
  isPublic = int(cache.hget(meeting_instance_key, 'isPublic'))
  if not(isPublic):
    email = cache.hget(f'user:{userID}', "email")
    audience = cache.lrange(f'{meeting_instance_key}:audience', 0, -1)
    if email not in audience:
      raise UserForbiddenToJoinMeeting('You are not allowed to join this meeting!')


def create_log(meeting_instance_key: str, userID: int, eventType: EventType):
  eventID = cache.incr('eventID')
  cache.hmset(f'log:{eventID}', {
    "userID": userID,
    "eventType": eventType,
    "timestamp": str(datetime.datetime.now())
  })
  cache.rpush(f'{meeting_instance_key}:logs', eventID)


@function.get('/meeting/{meetingID}/order/{orderID}/join')
def join_meeting_instance(meetingID: int, orderID: int, userID: int):
  try:
    meeting_instance_key = f'meeting:{meetingID}:order:{orderID}'

    check_if_meeting_exists(meeting_instance_key)
    check_if_user_already_in_meeting(meeting_instance_key, userID)
    check_if_user_forbidden_to_join_meeting(meeting_instance_key, userID)

    cache.rpush(f'{meeting_instance_key}:participants', userID)
    create_log(meeting_instance_key, userID, EventType.join)

    return {
      "success": True,
      "message": "Succefully joined the meeting."
    }
  except MeetingNotExistOrInactive as exc:
    raise HTTPException(400, str(exc))
  except UserForbiddenToJoinMeeting as exc:
    raise HTTPException(403, str(exc))
  except UserAlreadyInMeeting as exc:
    raise HTTPException(409, str(exc))
  except Exception as exc:
    exception_logger.exception(exc)
    raise HTTPException(500, "Failed to join the meeting.")


def check_if_user_not_in_meeting(meeting_instance_key: str, userID: int):
  participants = cache.lrange(f'{meeting_instance_key}:participants', 0, -1)
  if str(userID) not in participants:
    raise UserNotInMeeting('You are not attending this meeting.')


@function.get('/meeting/{meetingID}/order/{orderID}/leave')
def leave_meeting_instance(meetingID: int, orderID: int, userID: int):
  try:
    meeting_instance_key = f'meeting:{meetingID}:order:{orderID}'

    check_if_meeting_exists(meeting_instance_key)
    check_if_user_not_in_meeting(meeting_instance_key, userID)

    cache.lrem(f'{meeting_instance_key}:participants', 1, userID)
    create_log(meeting_instance_key, userID, EventType.leave)

    return {
      "success": True,
      "message": "Succefully left the meeting."
    }
  except MeetingNotExistOrInactive as exc:
    raise HTTPException(400, str(exc))
  except UserNotInMeeting as exc:
    raise HTTPException(409, str(exc))
  except Exception as exc:
    exception_logger.exception(exc)
    raise HTTPException(500, "Failed to leave the meeting.")


@function.get('/meeting/{meetingID}/order/{orderID}/participants')
def show_meeting_instance_participants(meetingID: int, orderID: int):
  try:
    meeting_instance_key = f'meeting:{meetingID}:order:{orderID}'

    check_if_meeting_exists(meeting_instance_key)

    response = []
    participants = cache.lrange(f'{meeting_instance_key}:participants', 0, -1)
    for userID in participants:
      name, age, gender, email = \
        cache.hmget(f'user:{userID}', ["name", "age", "gender", "email"])

      response.append({
        "name": name,
        "age": int(age),
        "gender": gender,
        "email": email
      })

    return { "participants": response }
  except MeetingNotExistOrInactive as exc:
    raise HTTPException(400, str(exc))
  except Exception as exc:
    exception_logger.exception(exc)
    raise HTTPException(500, "Failed to show the participants of the meeting.")


@function.get('/active-meetings')
def show_active_meetings():
  try:
    response = []
    active_meetings = cache.smembers('active_meetings')
    for meeting_instance_key in active_meetings:
      title, description, isPublic, start_time, finish_time = \
        cache.hmget(
          meeting_instance_key,
          ["title", "description", "isPublic", "fromdatetime", "todatetime"]
        )

      response.append({
        "title": title,
        "description": description,
        "isPublic": True if int(isPublic) else False,
        "fromdatetime": start_time,
        "todatetime": finish_time
      })

    return { "active_meetings": response }
  except Exception as exc:
    exception_logger.exception(exc)
    raise HTTPException(500, "Failed to show the active meetings.")


def create_message(meeting_instance_key: str, message: Message):
  messageID = cache.incr('messageID')
  cache.hmset(f'message:{messageID}', {
    "userID": message.userID,
    "body": message.body,
    "timestamp": str(datetime.datetime.now())
  })
  cache.rpush(f'{meeting_instance_key}:messages', messageID)


@function.post('/meeting/{meetingID}/order/{orderID}/message', status_code=201)
def post_message(message: Message, meetingID: int, orderID: int):
  try:
    meeting_instance_key = f'meeting:{meetingID}:order:{orderID}'

    check_if_meeting_exists(meeting_instance_key)
    check_if_user_not_in_meeting(meeting_instance_key, message.userID)

    create_message(meeting_instance_key, message)

    return {
      "success": True,
      "message": "Succefully posted the message."
    }
  except MeetingNotExistOrInactive as exc:
    raise HTTPException(400, str(exc))
  except UserNotInMeeting as exc:
    raise HTTPException(409, str(exc))
  except Exception as exc:
    exception_logger.exception(exc)
    raise HTTPException(500, "Failed to post the message.")


"""
The chronological order requirement is achieved automatically because lists are
ordered collections (they maintain the insertion order) & we are only appending
elements at the end of the list.
"""
@function.get('/meeting/{meetingID}/order/{orderID}/messages')
def show_meeting_instance_messages(meetingID: int, orderID: int):
  try:
    meeting_instance_key = f'meeting:{meetingID}:order:{orderID}'

    check_if_meeting_exists(meeting_instance_key)

    response = []
    messages = cache.lrange(f'{meeting_instance_key}:messages', 0, -1)
    for messageID in messages:
      userID, body, timestamp = \
        cache.hmget(f'message:{messageID}', ["userID", "body", "timestamp"])

      response.append({
        "userID": int(userID),
        "body": body,
        "timestamp": timestamp
      })

    return { "messages": response }
  except MeetingNotExistOrInactive as exc:
    raise HTTPException(400, str(exc))
  except Exception as exc:
    exception_logger.exception(exc)
    raise HTTPException(500, "Failed to show the messages of the meeting.")


def keep_latest_join_log_for_each_user(join_logs: List[Dict[str, Union[int, str]]]):
  idx_to_del = []
  userID_to_idx = dict()
  for idx, join_log in enumerate(join_logs[:]):
    userID = join_log["userID"]
    if userID in userID_to_idx:
      idx_to_del.append(userID_to_idx[userID])
    userID_to_idx[userID] = idx

  idx_to_del.sort(reverse=True)
  for idx in idx_to_del:
    del join_logs[idx]


@function.get('/active-meetings-participants-join-logs')
def show_active_meetings_participants_join_logs():
  try:
    response = []
    active_meetings = cache.smembers('active_meetings')
    for meeting_instance_key in active_meetings:
      title = cache.hget(meeting_instance_key, "title")
      participants = cache.lrange(f'{meeting_instance_key}:participants', 0, -1)

      join_logs = []
      logs = cache.lrange(f'{meeting_instance_key}:logs', 0, -1)
      for eventID in logs:
        userID, eventType, timestamp = \
          cache.hmget(f'log:{eventID}', ["userID", "eventType", "timestamp"])

        if userID in participants and eventType == EventType.join:
          join_logs.append({
            "userID": int(userID),
            "eventType": eventType,
            "timestamp": timestamp
          })

      keep_latest_join_log_for_each_user(join_logs)

      response.append({
        "meeting": title,
        "join_logs": join_logs
      })

    return { "active_meetings_participants_join_logs": response }
  except Exception as exc:
    exception_logger.exception(exc)
    raise HTTPException(
      500, "Failed to show the join logs of the participants in the active meetings.")


@function.get('/meeting/{meetingID}/order/{orderID}/user/{userID}/messages')
def show_meeting_instance_user_messages(meetingID: int, orderID: int, userID: int):
  try:
    meeting_instance_key = f'meeting:{meetingID}:order:{orderID}'

    check_if_meeting_exists(meeting_instance_key)

    response = []
    messages = cache.lrange(f'{meeting_instance_key}:messages', 0, -1)
    for messageID in messages:
      msg_userID, body, timestamp = \
        cache.hmget(f'message:{messageID}', ["userID", "body", "timestamp"])

      if str(userID) == msg_userID:
        response.append({
          "userID": int(msg_userID),
          "body": body,
          "timestamp": timestamp
        })

    return { "user_messages": response }
  except MeetingNotExistOrInactive as exc:
    raise HTTPException(400, str(exc))
  except Exception as exc:
    exception_logger.exception(exc)
    raise HTTPException(500, "Failed to show the messages of the user in the meeting.")
