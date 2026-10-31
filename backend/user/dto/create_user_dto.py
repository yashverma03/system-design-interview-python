from rest_framework import serializers
from user.models import UserRole


class CreateUserDto(serializers.Serializer):
  email = serializers.EmailField(required=True)
  name = serializers.CharField(required=True, max_length=255)
  password = serializers.CharField(required=True, write_only=True, min_length=8, max_length=128)
  role = serializers.ChoiceField(choices=UserRole.choices, required=False)
