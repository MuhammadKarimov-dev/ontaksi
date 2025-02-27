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
    print(f"Starting send_messages for announcement {announcement_id}")
    try:
        bot = TelegramBot()
        running = True
        
        while running:
            try:
                print("Checking announcement status")
                announcement = Announcement.objects.get(id=announcement_id)
                
                if not announcement.is_active:
                    print("Announcement is not active")
                    running = False
                    continue

                print("Getting active channels")
                channels = TelegramChannel.objects.filter(is_active=True)
                print(f"Found {channels.count()} active channels")
                
                for channel in channels:
                    try:
                        print(f"Sending message to channel: {channel.channel_id}")
                        success = bot.send_message_sync(channel.channel_id, announcement.message)
                        if success:
                            print(f"Successfully sent message to {channel.channel_id}")
                        else:
                            print(f"Failed to send message to {channel.channel_id}")
                    except Exception as e:
                        print(f"Error sending to channel {channel.channel_id}: {str(e)}")

                connection.close()
                print(f"Waiting for {announcement.interval} minutes")
                time.sleep(announcement.interval * 60)

            except Announcement.DoesNotExist:
                print("Announcement not found")
                running = False
            except Exception as e:
                print(f"Error in announcement loop: {str(e)}")
                time.sleep(5)

    except Exception as e:
        print(f"Error in send_messages: {str(e)}")