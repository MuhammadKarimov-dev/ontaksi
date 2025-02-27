import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Ilova joylashuvi to'g'ri ko'rsatilganligini tekshiramiz
print(f"BASE_DIR: {BASE_DIR}")
print(f"bot_manager path: {BASE_DIR / 'bot_manager'}")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'announcement.apps.AnnouncementConfig',
    'bot_manager.apps.BotManagerConfig',  # Qayta qo'shamiz
] 