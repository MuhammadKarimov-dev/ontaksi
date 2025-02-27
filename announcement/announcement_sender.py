import threading
import time
import asyncio
import logging
from bot_manager.telegram_bot import TelegramBot
from .models import Announcement, TelegramChannel
from django.contrib import messages
from django.core.cache import cache
from django.db import connection

# Logging ni sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

_local = threading.local()

def get_cache():
    if not hasattr(_local, 'cache'):
        _local.cache = cache
    return _local.cache

def send_messages(announcement_id):
    """Berilgan e'lonni Telegramga yuborish"""
    try:
        # Har bir thread uchun yangi event loop yaratish
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        bot = TelegramBot()
        running = True
        
        while running:
            try:
                # E'lonni bazadan qayta o'qiymiz
                announcement = Announcement.objects.get(id=announcement_id)
                
                if not announcement.is_active:
                    running = False
                    continue

                channels = TelegramChannel.objects.filter(is_active=True)
                success_count = 0
                fail_count = 0
                
                # Xabar yuborish
                for channel in channels:
                    try:
                        if bot.send_message_sync(channel.channel_id, announcement.message):
                            success_count += 1
                        else:
                            fail_count += 1
                    except Exception as e:
                        fail_count += 1
                        logger.error(f"Xatolik: {str(e)}")

                # Connection ni yopish
                connection.close()

                # Interval kutish
                time.sleep(announcement.interval * 60)

            except Announcement.DoesNotExist:
                running = False
            except Exception as e:
                logger.error(f"Xatolik: {str(e)}")
                time.sleep(5)

    except Exception as e:
        logger.error(f"Thread xatoligi: {str(e)}")
    
    finally:
        # Loop ni yopish
        if loop and not loop.is_closed():
            loop.close()
