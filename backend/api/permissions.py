from rest_framework.permissions import BasePermission


class IDKpermission(BasePermission):
    """https://dictionary.cambridge.org/dictionary/english/idk
       Никто не знает что это такое, если бы мы знали, но мы незнаем"""

    def has_permission(self, request, view):
        if view.action in ("destroy",
                           "partial_update",
                           "download_shopping_cart"):
            return request.user.is_authenticated
        else:
            return (request.method in ('GET', 'HEAD', 'OPTIONS')
                    or request.user.is_authenticated)

    def has_object_permission(self, request, view, recipe):
        return recipe.author == request.user
