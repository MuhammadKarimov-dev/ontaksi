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
        bot = TelegramBot()  # Singleton instance
        running = True
        
        while running:
            try:
                # E'lonni bazadan qayta o'qiymiz
                announcement = Announcement.objects.get(id=announcement_id)
                
                if not announcement.is_active:
                    running = False
                    continue

                channels = TelegramChannel.objects.filter(is_active=True)
                
                # Xabar yuborish
                for channel in channels:
                    try:
                        logger.info(f"Sending message to channel {channel.channel_id}")
                        success = bot.send_message_sync(channel.channel_id, announcement.message)
                        if success:
                            logger.info(f"Message sent successfully to {channel.channel_id}")
                        else:
                            logger.error(f"Failed to send message to {channel.channel_id}")
                    except Exception as e:
                        logger.error(f"Error sending message to {channel.channel_id}: {str(e)}")

                # Connection ni yopish
                connection.close()

                # Interval kutish
                time.sleep(announcement.interval * 60)

            except Announcement.DoesNotExist:
                running = False
            except Exception as e:
                logger.error(f"Error in announcement loop: {str(e)}")
                time.sleep(5)

    except Exception as e:
        logger.error(f"Error in send_messages: {str(e)}")