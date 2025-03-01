from django.db import models
from django.contrib.auth.models import User
import re

class Announcement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    interval = models.IntegerField(default=5)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'announcements'

class TelegramChannel(models.Model):
    TYPES = (
        ('channel', 'Kanal'),
        ('group', 'Guruh'),
    )
    
    channel_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPES, default='channel')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Kanalni tozalash va formatlash
        channel = self.channel_id.strip()
        
        # https://t.me/username formatini tekshirish
        tme_match = re.match(r'https?://t\.me/([a-zA-Z]\w{3,30}[a-zA-Z\d])', channel)
        if tme_match:
            self.channel_id = '@' + tme_match.group(1)
            return

        # @username formatini tekshirish
        username_match = re.match(r'@?([a-zA-Z]\w{3,30}[a-zA-Z\d])', channel)
        if username_match:
            self.channel_id = '@' + username_match.group(1)
            return

        # Raqamli ID bo'lsa
        if channel.lstrip('-').isdigit():
            self.channel_id = channel
            return

        raise ValueError("Noto'g'ri kanal/guruh formati. Username (@username), "
                      "t.me havolasi yoki ID raqami bo'lishi kerak.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        type_name = 'Kanal' if self.type == 'channel' else 'Guruh'
        return f"{self.name} ({type_name})"


