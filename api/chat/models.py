from django.db import models


class Chat(models.Model):
    text = models.TextField()
    sender = models.CharField(max_length=88)
    datetime = models.DateTimeField(auto_now_add=True)
