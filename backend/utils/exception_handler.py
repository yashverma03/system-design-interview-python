import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from utils.exceptions import BaseAPIException

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
  """Formats every error as {message, error?}."""
  request = context.get('request')
  where = f' ({request.method} {request.path})' if request else ''
  logger.error(f'{type(exc).__name__} - {exc}{where}', exc_info=exc)

  if isinstance(exc, BaseAPIException):
    data = {'message': str(exc.detail)}
    if exc.error is not None:
      data['error'] = exc.error
    return Response(data, status=exc.status_code)

  response = exception_handler(exc, context)
  if response is None:
    return Response({'message': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  if isinstance(response.data, dict):
    return Response({'message': 'Validation error', 'error': response.data}, status=response.status_code)
  return Response({'message': str(response.data)}, status=response.status_code)
