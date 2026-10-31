from functools import wraps

from user.models import UserRole
from utils.exceptions import ForbiddenException


def roles(allowed_roles: list[UserRole]):
  """Restricts a view to the given roles. Apply below @api_view so DRF handles the exception."""
  allowed = [role.value for role in allowed_roles]

  def decorator(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
      user_role = getattr(getattr(request, 'jwt_user', None), 'role', None)
      if user_role not in allowed:
        raise ForbiddenException(f'Access denied. Required roles: {", ".join(allowed)}')
      return view_func(request, *args, **kwargs)

    return wrapped

  return decorator
