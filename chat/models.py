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

    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    is_ai = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message in {self.room.name} by {self.sender or 'AI'}"

class AgentProfile(models.Model):
    name = models.CharField(max_length=20, unique=True)  # e.g., "june", "ludwig"
    description = models.TextField(blank=True)
    model_name = models.CharField(max_length=200, default="facebook/bart-large-cnn")  # Hugging Face model name
    summary_min_length = models.IntegerField(default=30)
    summary_max_length = models.IntegerField(default=150)
    # Add other settings as needed (e.g., top_p, frequency_penalty, presence_penalty)

    def __str__(self):
        return self.name