from .thread_manager import ThreadManager
from .error_handler import with_retry, ErrorHandler
from monitoring.monitor import SystemMonitor
from bot_manager.bot import TelegramBot
import logging
import time

class MessageService:
    def __init__(self):
        self.thread_manager = ThreadManager()
        self.monitor = SystemMonitor()
        self.bot = TelegramBot()
    
    @with_retry(max_retries=3)
    @ErrorHandler.handle_telegram_error
    def send_message(self, channel_id, message):
        """Xabar yuborish"""
        return self.bot.send_message(channel_id, message)
    
    def start_announcement(self, announcement):
        """E'lonni boshlash"""
        def announcement_task():
            while True:
                try:
                    if not announcement.is_active:
                        break
                        
                    channels = announcement.channels.filter(is_active=True)
                    for channel in channels:
                        self.send_message(channel.channel_id, announcement.message)
                        
                    time.sleep(announcement.interval * 60)
                except Exception as e:
                    logging.error(f"Announcement {announcement.id} error: {str(e)}")
                    raise
        
        self.thread_manager.start_task(announcement.id, announcement_task) 