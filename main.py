import os
import sys
import django
import multiprocessing

# Django sozlamalarini o'rnatish
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taxi_site.settings')
django.setup()

from bot_manager.bot import TelegramBot
from django.core.management import execute_from_command_line

def run_django():
    execute_from_command_line(['manage.py', 'runserver'])

def run_bot():
    try:
        bot = TelegramBot()
        bot.start()
    except KeyboardInterrupt:
        if bot:
            bot.stop()
    except Exception as e:
        print(f"Bot xatoligi: {e}")

if __name__ == '__main__':
    try:
        # Django va bot jarayonlarini yaratish
        django_process = multiprocessing.Process(target=run_django)
        bot_process = multiprocessing.Process(target=run_bot)

        # Jarayonlarni boshlash
        django_process.start()
        bot_process.start()

        # Jarayonlarni kutish
        django_process.join()
        bot_process.join()

    except KeyboardInterrupt:
        print("\nServer to'xtatildi")
        sys.exit(0)
