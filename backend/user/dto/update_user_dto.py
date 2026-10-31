from rest_framework import serializers
from user.models import UserRole


class UpdateUserDto(serializers.Serializer):
  name = serializers.CharField(required=False, max_length=255)
  password = serializers.CharField(required=False, write_only=True, min_length=8, max_length=128)
  role = serializers.ChoiceField(choices=UserRole.choices, required=False)
