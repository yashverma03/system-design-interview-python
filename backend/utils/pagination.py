from rest_framework import serializers


class PaginationDto(serializers.Serializer):
  page = serializers.IntegerField(required=False, min_value=1, default=1)
  limit = serializers.IntegerField(required=False, min_value=1, max_value=100, default=10)


def paginate(queryset, page: int, limit: int) -> dict:
  total = queryset.count()
  offset = (page - 1) * limit
  return {
    'items': list(queryset[offset:offset + limit]),
    'page': page,
    'limit': limit,
    'total': total,
    'total_pages': (total + limit - 1) // limit,
  }
