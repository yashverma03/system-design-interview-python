from rest_framework import serializers


class EmailPasswordDto(serializers.Serializer):
  email = serializers.EmailField(required=True)
  password = serializers.CharField(required=True, write_only=True)
