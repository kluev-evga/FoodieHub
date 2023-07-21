from rest_framework.permissions import BasePermission


class IsOwnerOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, recipe):
        return recipe.author == request.user
