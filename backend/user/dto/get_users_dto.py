from rest_framework import serializers
from utils.pagination import PaginationDto


class GetUsersDto(PaginationDto):
  search = serializers.CharField(required=False, allow_blank=True)
