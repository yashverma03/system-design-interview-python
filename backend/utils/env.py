import os


def get_env(name: str) -> str:
  value = os.getenv(name)
  if value is None or value == '':
    raise ValueError(f'Environment variable {name} is not set or is empty. Please set it in your .env file.')
  return value
