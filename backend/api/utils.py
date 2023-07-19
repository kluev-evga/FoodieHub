from django.utils.translation import gettext_lazy as translate
from rest_framework.response import Response
from rest_framework import serializers


def perform_create_or_delte(pk, request, model, post_serializer, destroy_serializer):
    arguments = {"data": {"recipe": pk}, "context": {"request": request}}

    if request.method == "POST":
        serializer = post_serializer(**arguments)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    serializer = destroy_serializer(**arguments)
    serializer.is_valid(raise_exception=True)
    instance = model.objects.filter(user=request.user, recipe_id=pk)
    if not instance:
        return Response({"message": translate("not exist")}, status=400)
    instance.delete()
    return Response(status=204)


class QueryParamsSerializer(serializers.Serializer):
    recipes_limit = serializers.IntegerField(min_value=0)


def validate_limit(limit):
    if limit:
        serializer = QueryParamsSerializer(data={"recipes_limit": limit})
        serializer.is_valid(raise_exception=True)
