from django.db import migrations
from django.contrib.auth.models import User

def create_default_announcement(apps, schema_editor):
    Announcement = apps.get_model('announcement', 'Announcement')
    User = apps.get_model('auth', 'User')
    
    # Agar xabar mavjud bo'lmasa, yangi yaratamiz
    if not Announcement.objects.exists():
        # Default admin foydalanuvchisi
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            
        Announcement.objects.create(
            user=admin_user,
            message="Yangi e'lon matni",
            interval=60,
            is_active=False
        )

def reverse_default_announcement(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('announcement', '0001_initial'),  # O'zingizning oxirgi migratsiya faylingizga moslashtiring
    ]

    operations = [
        migrations.RunPython(create_default_announcement, reverse_default_announcement),
    ] 