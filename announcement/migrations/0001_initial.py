# Generated by Django 5.1.5 on 2025-02-17 13:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramChannel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_id', models.CharField(max_length=100, unique=True)),
                ('channel_name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(choices=[('toshkent_andijon', 'Toshkentdan Andijonga'), ('andijon_toshkent', 'Andijondan Toshkentga')], max_length=20)),
                ('time', models.DateTimeField()),
                ('member', models.IntegerField(choices=[(1, "1 ta yo'lovchi"), (2, "2 ta yo'lovchi"), (3, "3 ta yo'lovchi"), (4, "4 ta yo'lovchi"), (5, "5 ta yo'lovchi"), (6, "6 ta yo'lovchi"), (7, "7 ta yo'lovchi"), (8, "8 ta yo'lovchi"), (9, "9 ta yo'lovchi"), (10, "10 ta yo'lovchi")])),
                ('women', models.BooleanField(default=False)),
                ('phone', models.CharField(max_length=15)),
                ('interval', models.IntegerField(default=5)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
