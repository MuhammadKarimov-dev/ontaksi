from django.db import models
from django.utils import timezone
import datetime

class VerificationCode(models.Model):
    class Meta:
        app_label = 'bot_manager'
        db_table = 'bot_manager_verificationcode'
        
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phone_number} - {self.code}"

    def is_expired(self):
        """Kod 10 daqiqadan ko'p vaqt oldin yaratilgan bo'lsa, eskirgan hisoblanadi"""
        return timezone.now() - self.created_at > datetime.timedelta(minutes=10) 