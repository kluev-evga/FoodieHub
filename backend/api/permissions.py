from rest_framework.permissions import BasePermission


# Вынес action - но откатил назад
# потому что это выглядит не читабельно

# не возможно понять как это работает
# не возможно придумать название, я назвал это I_dont_know_permission
# не возможно понять какие права у отдельных эндпоинтов (их 10 штук)

# у исходного варианта - все 3 пункта == easy

# class IDKpermission(BasePermission):
#     """Никто не знает что это такое, если бы мы знали, но мы незнаем"""
#
#     def has_permission(self, request, view):
#         if view.action in ("destroy",
#                            "partial_update",
#                            "download_shopping_cart"):
#             return request.user.is_authenticated
#         else:
#             return (request.method in ('GET', 'HEAD', 'OPTIONS')
#                     or request.user.is_authenticated)
#
#     def has_object_permission(self, request, view, recipe):
#         return view.action == "retrieve" or recipe.author == request.user


class IsOwnerOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, recipe):
        return recipe.author == request.user
