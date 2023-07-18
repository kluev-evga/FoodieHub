from rest_framework import serializers


class QueryParamsSerializer(serializers.Serializer):
    recipes_limit = serializers.IntegerField(min_value=0)


def validate_limit(limit):
    if limit:
        serializer = QueryParamsSerializer(data={"recipes_limit": limit})
        serializer.is_valid(raise_exception=True)
