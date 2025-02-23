from django.db import models
from django.contrib.auth.models import User

class TelegramChannel(models.Model):
    channel_id = models.CharField(max_length=100, unique=True)
    channel_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.channel_name

class Announcement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    interval = models.IntegerField(default=5)
    
    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}..."

