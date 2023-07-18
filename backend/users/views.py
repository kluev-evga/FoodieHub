from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscribe
from users.serializers import SubscribeSerializer, SubscriptionsSerializer
from users.utils import validate_limit

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    activation = None
    resend_activation = None
    reset_password = None
    reset_password_confirm = None
    set_username = None
    reset_username = None
    reset_username_confirm = None

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(methods=["get"], detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        limit = request.query_params.get("recipes_limit")
        validate_limit(limit)
        queryset = User.objects.filter(subscription__subscriber=request.user)
        serializer = SubscriptionsSerializer(
            context={"request": request, "limit": limit},
            instance=self.paginate_queryset(queryset),
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=["post", "delete"], detail=True, permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        get_object_or_404(User, pk=id)
        data = {"subscriber": request.user.pk, "subscription": id}

        if request.method == "POST":
            limit = request.query_params.get("recipes_limit")
            validate_limit(limit)
            serializer = SubscribeSerializer(
                context={"request": request, "limit": limit},
                data=data
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        instance = Subscribe.objects.filter(**data)
        if instance:
            instance.delete()
            return Response(status=204)

        return Response({"message": "Подписки не существует"}, status=400)
