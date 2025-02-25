import threading
import time
from bot_manager.telegram_bot import TelegramBot
from .models import Announcement, TelegramChannel

bot = TelegramBot()

def send_messages(announcement_id):
    """Berilgan e’lonni Telegramga yuborish"""
    while True:
        try:
            announcement = Announcement.objects.filter(id=announcement_id).first()

            # Agar e’lon o‘chirilgan bo‘lsa yoki to‘xtatilgan bo‘lsa, thread tugaydi
            if announcement is None or not announcement.is_active:
                print(f"⏹ E’lon to‘xtatildi yoki o‘chirildi: {announcement_id}")
                break  

            channels = TelegramChannel.objects.filter(is_active=True)

            for channel in channels:
                bot.send_message_sync(channel.channel_id, announcement.message)
                print(f"✅ Xabar yuborildi: {channel.channel_id}")

            time.sleep(0.5)  # Xabar yuborish oralig‘i

        except Exception as e:
            print(f"❌ Xato: {e}")
            time.sleep(5)  # Xato bo‘lsa, 5 soniya kutish
