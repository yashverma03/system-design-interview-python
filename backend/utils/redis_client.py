"""
Redis helper. Not used anywhere yet; import when needed:

    from utils.redis_client import redis_set, redis_get
"""
import json
from typing import Any

import redis
from utils.env import get_env

redis_client = redis.Redis(
  host=get_env('REDIS_HOST'),
  port=int(get_env('REDIS_PORT')),
  decode_responses=True,
)


def redis_get(key: str) -> Any | None:
  value = redis_client.get(key)
  return json.loads(value) if value is not None else None


def redis_set(key: str, value: Any, ttl_seconds: int | None = None) -> None:
  redis_client.set(key, json.dumps(value, default=str), ex=ttl_seconds)


def redis_delete(key: str) -> None:
  redis_client.delete(key)
