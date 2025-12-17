from django.db import models

from user.models import User


class Chat(models.Model):
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    label = models.CharField(max_length=255, blank=True)
