from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, null=True)
    telegram_id = models.BigIntegerField(unique=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
    )

    def __str__(self):
        return f"{self.username} ({self.phone_number})"

class Message(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    sent_via_telegram = models.BooleanField(default=False)
    sent_via_sms = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Xabar: {self.text[:30]}..."

class Channel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    channel_username = models.CharField(max_length=100)  # @ bilan kanal username
    channel_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.channel_name} (@{self.channel_username})"

class Announcement(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    channels = models.ManyToManyField(Channel)
    interval = models.IntegerField(default=5)  # minutlarda
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

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

class PhoneNumber(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Telefon raqami +998912345678 formatida bo'lishi kerak"
    )
    number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        unique=True,
        verbose_name="Telefon raqam"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Telefon raqam"
        verbose_name_plural = "Telefon raqamlar"

class SMSVerification(models.Model):
    phone_number = models.CharField(max_length=15)
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.phone_number} - {self.sent_at}"


