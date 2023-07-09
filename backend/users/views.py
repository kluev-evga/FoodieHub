from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action


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
