from django.core.management.base import BaseCommand
from announcement.models import Announcement, TelegramChannel, ActiveTask
from bot_manager.telegram_bot import TelegramBot
import time

class Command(BaseCommand):
    help = 'Send announcements to Telegram channels'
    
    def __init__(self):
        super().__init__()
        self.bot = TelegramBot()
        
    def add_task(self, announcement_id):
        ActiveTask.objects.create(
            announcement_id=announcement_id,
            is_active=True
        )
        
    def stop_task(self, announcement_id):
        ActiveTask.objects.filter(
            announcement_id=announcement_id,
            is_active=True
        ).update(is_active=False)
            
    def send_messages(self, announcement_id):
        while ActiveTask.objects.filter(
            announcement_id=announcement_id,
            is_active=True
        ).exists():
            try:
                announcement = Announcement.objects.get(id=announcement_id)
                channels = TelegramChannel.objects.filter(is_active=True)
                
                for channel in channels:
                    self.bot.send_message_sync(channel.channel_id, announcement.message)
                    self.stdout.write(f"✅ Xabar yuborildi: {channel.channel_id}")
                
                time.sleep(announcement.interval * 60)
            except Exception as e:
                self.stdout.write(f"❌ Xato: {e}")
                time.sleep(5)
                
    def handle(self, *args, **options):
        announcement_id = options.get('announcement_id')
        action = options.get('action')
        
        if action == 'start':
            self.add_task(announcement_id)
            self.send_messages(announcement_id)
        elif action == 'stop':
            self.stop_task(announcement_id)
            
    def add_arguments(self, parser):
        parser.add_argument('action', type=str, help="start yoki stop")
        parser.add_argument('announcement_id', type=int, help="E'lon ID raqami")