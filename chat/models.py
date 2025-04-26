from django.db import models
from django.contrib.auth.models import User

class ChatRoom(models.Model):
    name = models.CharField(max_length=100)
    agent = models.CharField(
        max_length=20,
        choices=[
            ("june", "June"),
            ("ludwig", "Ludwig"),
            ("gustav", "Gustav"),
            ("salvador", "Salvador"),
        ],
        default="june"
    )

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    is_ai = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)