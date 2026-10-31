from django.utils.deprecation import MiddlewareMixin


class CsrfExemptMiddleware(MiddlewareMixin):
  """API endpoints use JWT, so CSRF checks are skipped for /api/."""

  def process_request(self, request):
    if request.path.startswith('/api/'):
      setattr(request, '_dont_enforce_csrf_checks', True)
    return None
