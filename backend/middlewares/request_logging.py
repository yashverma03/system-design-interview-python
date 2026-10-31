import logging
import time

logger = logging.getLogger('request')


class RequestLoggingMiddleware:
  """Logs method, path, status and duration for every request."""

  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    start = time.perf_counter()
    response = self.get_response(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(f'{request.method} {request.path} {response.status_code} {duration_ms:.1f}ms')
    return response
