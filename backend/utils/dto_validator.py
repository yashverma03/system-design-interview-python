from rest_framework import serializers
from utils.exceptions import BadRequestException


class DTOValidator:
  @staticmethod
  def validate(dto_class: type[serializers.Serializer], data: dict) -> dict:
    dto = dto_class(data=data)
    if not dto.is_valid():
      raise BadRequestException(detail='Bad Request Exception', error=dto.errors)
    return dto.validated_data
