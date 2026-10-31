from django.db import models


class EnumField(models.Field):
  """Postgres enum column. The enum type must exist (see user migration)."""

  def __init__(self, enum_type: str, *args, **kwargs):
    self.enum_type = enum_type
    super().__init__(*args, **kwargs)

  def db_type(self, connection):
    return self.enum_type

  def deconstruct(self):
    name, path, args, kwargs = super().deconstruct()
    kwargs['enum_type'] = self.enum_type
    return name, path, args, kwargs
