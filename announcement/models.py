from django.db import models
from django.contrib.auth.models import User

class Announcement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    price = models.CharField(max_length=50, blank=True, null=True)
    interval = models.IntegerField(default=5)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}"

    class Meta:
        db_table = 'announcements'

class TelegramChannel(models.Model):
    channel_id = models.CharField(max_length=100)
    channel_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'telegram_channels'


