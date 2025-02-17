from django.db import models
from django.contrib.auth.models import User

class TelegramChannel(models.Model):
    channel_id = models.CharField(max_length=100, unique=True)
    channel_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.channel_name

class Announcement(models.Model):
    ADDRESS_CHOICES = (
        ('toshkent_andijon', 'Toshkentdan Andijonga'),
        ('andijon_toshkent', 'Andijondan Toshkentga'),
    )
    
    MEMBER_CHOICES = (
        (1, '1 ta yo\'lovchi'),
        (2, '2 ta yo\'lovchi'),
        (3, '3 ta yo\'lovchi'),
        (4, '4 ta yo\'lovchi'),
        (5, '5 ta yo\'lovchi'),
        (6, '6 ta yo\'lovchi'),
        (7, '7 ta yo\'lovchi'),
        (8, '8 ta yo\'lovchi'),
        (9, '9 ta yo\'lovchi'),
        (10, '10 ta yo\'lovchi'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=20, choices=ADDRESS_CHOICES)
    time = models.DateTimeField()
    member = models.IntegerField(choices=MEMBER_CHOICES)
    women = models.BooleanField(default=False)
    phone = models.CharField(max_length=15)
    interval = models.IntegerField(default=5)
    
    def __str__(self):
        return f"{self.address} - {self.time}"

