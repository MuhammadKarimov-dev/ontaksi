import threading
import time
import logging
from bot_manager.bot import TelegramBot
from .models import Announcement, TelegramChannel
from django.db import connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def send_messages(announcement_id):
    """Berilgan e'lonni Telegramga yuborish"""
    try:
        bot = TelegramBot()
        running = True
        
        while running:
            try:
                announcement = Announcement.objects.get(id=announcement_id)
                
                if not announcement.is_active:
                    running = False
                    continue

                channels = TelegramChannel.objects.filter(is_active=True)
                
                for channel in channels:
                    try:
                        logger.info(f"Channel {channel.channel_id} ga xabar yuborilmoqda")
                        success = bot.send_message_sync(channel.channel_id, announcement.message)
                        if success:
                            logger.info(f"Xabar muvaffaqiyatli yuborildi: {channel.channel_id}")
                        else:
                            logger.error(f"Xabar yuborish muvaffaqiyatsiz: {channel.channel_id}")
                    except Exception as e:
                        logger.error(f"Xabar yuborishda xatolik ({channel.channel_id}): {str(e)}")

                connection.close()
                time.sleep(announcement.interval * 60)

            except Announcement.DoesNotExist:
                running = False
            except Exception as e:
                logger.error(f"E'lon tsiklida xatolik: {str(e)}")
                time.sleep(5)

    except Exception as e:
        logger.error(f"Xabar yuborishda umumiy xatolik: {str(e)}")