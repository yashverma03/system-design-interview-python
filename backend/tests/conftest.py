import os
import uuid
from types import SimpleNamespace

import pytest

# Must be set before Django settings are imported (settings read these via get_env).
os.environ.update({
  'DJANGO_SECRET_KEY': 'test-secret-key',
  'DJANGO_DEBUG': 'False',
  'DB_USERNAME': 'test',
  'DB_PASSWORD': 'test',
  'DB_DATABASE': 'test',
  'DB_HOST': 'localhost',
  'DB_PORT': '5432',
  'REDIS_HOST': 'localhost',
  'REDIS_PORT': '6379',
  'JWT_SECRET_KEY': 'test-jwt-secret-with-at-least-32-bytes',
  'JWT_EXPIRY_DAYS': '7',
})


@pytest.fixture
def sample_user():
  return SimpleNamespace(
    id=uuid.uuid4(),
    email='jane@example.com',
    name='Jane',
    role='manager',
    password='hashed',
  )
