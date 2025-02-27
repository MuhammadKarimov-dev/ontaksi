import logging
import time
from bot_manager.bot import TelegramBot
from .models import Announcement, TelegramChannel

logger = logging.getLogger(__name__)

def send_messages(announcement_id):
    """Berilgan e'lonni Telegramga yuborish"""
    try:
        # E'lonni olish va faolligini tekshirish
        announcement = Announcement.objects.get(id=announcement_id)
        if not announcement.is_active:
            logger.info(f"E'lon {announcement_id} faol emas, yuborish to'xtatildi")
            return

        channels = TelegramChannel.objects.filter(is_active=True)
        bot = TelegramBot()
        
        for channel in channels:
            # Har bir xabar yuborishdan oldin e'lonning faolligini qayta tekshirish
            announcement.refresh_from_db()
            if not announcement.is_active:
                logger.info(f"E'lon {announcement_id} yuborish jarayonida o'chirildi")
                return

            try:
                success = bot.send_message(channel.channel_id, announcement.message)
                if success:
                    logger.info(f"Xabar yuborildi: {channel.channel_id}")
                else:
                    logger.error(f"Xabar yuborilmadi: {channel.channel_id}")
                    # Xabar yuborilmagan kanallarni qayta urinish logikasini qo'shish mumkin
            except Exception as channel_error:
                logger.error(f"Kanal {channel.channel_id} ga yuborishda xatolik: {str(channel_error)}")
                continue

            # Intervalda kutish
            time.sleep(announcement.interval)
            
    except Announcement.DoesNotExist:
        logger.error(f"E'lon topilmadi: {announcement_id}")
    except Exception as e:
        logger.error(f"send_messages da xatolik: {str(e)}")

def send_sms(phone_number, code):
    """Telefon raqamiga tasdiqlash kodini yuborish"""
    # SMS yuborish logikasi
    print(f"SMS yuborildi: {phone_number} raqamiga {code} kodi")