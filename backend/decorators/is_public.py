def is_public(view_func):
  """Marks a view as public so JWTAuthMiddleware skips it. Apply above @api_view."""
  view_func._is_public = True
  return view_func
