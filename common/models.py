from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

class FailedLogin(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )
    provided_username = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class CustomizedUser(AbstractUser):
    pass