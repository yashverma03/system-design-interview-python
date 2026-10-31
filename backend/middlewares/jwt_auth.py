from types import SimpleNamespace

import jwt
from django.conf import settings
from django.http import JsonResponse
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from utils.exceptions import UnauthorizedException


class JWTAuthMiddleware(MiddlewareMixin):
  """
  Global JWT auth. Every route requires `Authorization: Bearer <token>`
  unless its view is marked with @is_public. The decoded payload is
  exposed as request.jwt_user.
  """

  SKIP_PREFIXES = ('/admin', '/static')

  def process_request(self, request):
    if request.method == 'OPTIONS' or request.path.startswith(self.SKIP_PREFIXES):
      return None

    try:
      view_func = resolve(request.path).func
      if getattr(view_func, '_is_public', False):
        return None
    except Exception:
      pass

    parts = request.META.get('HTTP_AUTHORIZATION', '').split(' ')
    if len(parts) != 2 or parts[0].lower() != 'bearer':
      return self._unauthorized('Authentication required. Use: Bearer <token>')

    try:
      payload = jwt.decode(parts[1], settings.JWT_SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
      return self._unauthorized('Token has expired.')
    except jwt.InvalidTokenError:
      return self._unauthorized('Invalid token.')

    if not payload.get('user_id'):
      return self._unauthorized('Invalid token payload.')

    request.jwt_user = SimpleNamespace(**payload)
    return None

  def _unauthorized(self, message):
    exc = UnauthorizedException(message)
    return JsonResponse({'message': str(exc.detail)}, status=exc.status_code)
