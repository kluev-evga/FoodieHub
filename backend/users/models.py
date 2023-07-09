from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Subscribe(models.Model):
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptions")
    subscription = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "api_subscribe"
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscription'],
                name='unique_subscriber_subscription')
        ]
