import os
import redis

redis_host = os.environ.get('REDIS_HOST')
redis_password = os.environ.get('REDIS_PASSWORD')

cache = redis.Redis(
  host=redis_host,
  password=redis_password,
  decode_responses=True
)
