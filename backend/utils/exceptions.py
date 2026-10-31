from rest_framework import status
from rest_framework.exceptions import APIException


class BaseAPIException(APIException):
  status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
  default_detail = 'A server error occurred.'
  default_code = 'error'

  def __init__(self, detail=None, code=None, status_code=None, error=None):
    if status_code is not None:
      self.status_code = status_code
    self.error = error
    super().__init__(detail, code)


class ConflictException(BaseAPIException):
  status_code = status.HTTP_409_CONFLICT
  default_detail = 'Resource conflict occurred.'
  default_code = 'conflict'


class NotFoundException(BaseAPIException):
  status_code = status.HTTP_404_NOT_FOUND
  default_detail = 'Resource not found.'
  default_code = 'not_found'


class BadRequestException(BaseAPIException):
  status_code = status.HTTP_400_BAD_REQUEST
  default_detail = 'Bad request.'
  default_code = 'bad_request'


class UnauthorizedException(BaseAPIException):
  status_code = status.HTTP_401_UNAUTHORIZED
  default_detail = 'Authentication required.'
  default_code = 'unauthorized'


class ForbiddenException(BaseAPIException):
  status_code = status.HTTP_403_FORBIDDEN
  default_detail = 'Access denied.'
  default_code = 'forbidden'
