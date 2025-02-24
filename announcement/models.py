from django.db import models
from django.contrib.auth.models import User

class Announcement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    interval = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'announcements'

class TelegramChannel(models.Model):
    channel_id = models.CharField(max_length=100)
    channel_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'telegram_channels'

class ActiveTask(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'active_tasks'

