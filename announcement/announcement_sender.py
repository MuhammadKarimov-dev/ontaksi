import threading
import time
import asyncio
from pyrogram import Client
from django.db import transaction
from asgiref.sync import sync_to_async
from .models import Announcement, TelegramChannel
import logging
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

# Telegram API credentials
API_ID = '27075572'
API_HASH = '1b56557db16cca997768fe87a724e75b'
SESSION_STRING = 'AgGdI_QAKOQSmLz6qF6ewBelgymYCmk76TXX4vBSQG3-oUYyxybu2tNykk__e9Fza5fIj1j-wI9HMqz-XFY7pHj82PPuYvocel2Ww9rOH8A_AhWWMfRHqN1ZhdlAbQUPV0jSDfxCvtjoplS4kImeHxFZ3I6obYCBOjHO_cOUXzHWBc6fhrRZvj4TiO47vsqd1a_dzl0m3Duni8DFZjvG9G3NjRw3RhBlREUYY7pcHkmkIZOOSJaRnAbVScRcpCNT5w4wKI5G5vo9g9zZnNrcwq6FKehA03DMvtk8cceLtCLD8xNyJeSqABAeZ4rpRVkIXEzRbweYLOzxbPx-H6aXuMqGQOy5MgAAAAANJISAAA'  # get_session.py dan olgan REAL session stringni qo'ying

MAX_RETRIES = 3  # Maksimal qayta urinishlar soni
RETRY_DELAY = 10  # Qayta urinish oralig'i (sekund)

# Yuborilmagan xabarlarni saqlash uchun
pending_messages = {}

async def send_message_async(app, channel, message):
    try:
        chat_id = channel.channel_id
        
        # Kanal ID ni tozalash
        if isinstance(chat_id, str):
            if chat_id.startswith('-100'):
                chat_id = int(chat_id)
            elif not chat_id.startswith('@'):
                chat_id = '@' + chat_id
                
        # Avval yuborilmagan xabarlar bo'lsa, ularni yuborish
        if chat_id in pending_messages:
            await app.send_message(
                chat_id=chat_id,
                text=pending_messages[chat_id],
                parse_mode=None
            )
            print(f"✅ Avvalgi yuborilmagan xabar yuborildi: {channel.channel_id}")
            del pending_messages[chat_id]
            await asyncio.sleep(2)
                
        await app.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=None
        )
        print(f"✅ Xabar yuborildi: {channel.channel_id}")
        await asyncio.sleep(2)
        
    except Exception as e:
        error_message = str(e).lower()
        print(f"❌ Xabar yuborilmadi: {channel.channel_id} - {str(e)}")
        
        if "slowmode" in error_message:
            # Xabarni keyingi safar yuborish uchun saqlab qo'yamiz
            pending_messages[chat_id] = message
            print(f"⏳ Xabar keyingi safar yuboriladi: {channel.channel_id}")
            
        elif isinstance(e, (TimeoutError, ConnectionError)):
            # Boshqa xatoliklar uchun ham saqlab qo'yamiz
            pending_messages[chat_id] = message
            logger.warning(f"Xatolik yuz berdi, keyingi safar qayta uriniladi")

def get_announcement(announcement_id):
    try:
        with transaction.atomic():
            return Announcement.objects.filter(id=announcement_id).first()
    except Exception as e:
        print(f"❌ Announcement olishda xato: {e}")
        return None

def get_active_channels():
    try:
        with transaction.atomic():
            return list(TelegramChannel.objects.filter(is_active=True))
    except Exception as e:
        print(f"❌ Kanallarni olishda xato: {e}")
        return []

def get_event_loop():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

async def send_messages_async(app, channels, message):
    """Barcha kanallarga xabar yuborish"""
    tasks = []
    for channel in channels:
        task = asyncio.create_task(send_message_async(app, channel, message))
        tasks.append(task)
    
    # ignore_exceptions=True qo'shamiz
    await asyncio.gather(*tasks, return_exceptions=True)

async def run_client(announcement_id):
    """Pyrogram client ni ishga tushirish"""
    try:
        # Django ORM ni sync_to_async bilan o'rab olish
        get_announcement = sync_to_async(Announcement.objects.get)
        get_channels = sync_to_async(lambda: list(TelegramChannel.objects.filter(is_active=True)))
        save_announcement = sync_to_async(lambda x: x.save())

        announcement = await get_announcement(id=announcement_id)
        if not announcement.is_active:
            logger.info(f"Announcement {announcement_id} is not active")
            return

        channels = await get_channels()
        
        async with Client(
            "my_account",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=SESSION_STRING
        ) as app:
            await send_messages_async(app, channels, announcement.message)

        # Keyingi yuborish vaqtini yangilash
        announcement.last_sent = datetime.now()
        await save_announcement(announcement)

    except Exception as e:
        logger.error(f"Error in run_client: {str(e)}")

def send_messages(announcement_id):
    """Barcha kanallarga xabar yuborish"""
    try:
        loop = get_event_loop()
        loop.run_until_complete(run_client(announcement_id))
    except Exception as e:
        logger.error(f"Error in send_messages: {str(e)}")

def start_announcement_thread(announcement_id, message=None):
    """Xabarni yuborish jarayonini boshlash"""
    print(f"📝 E'lon yuborish boshlandi: {message[:30] if message else ''}...")
    
    def run_thread():
        while True:
            try:
                announcement = Announcement.objects.get(id=announcement_id)
                if not announcement.is_active:
                    logger.info(f"Announcement {announcement_id} stopped")
                    break

                send_messages(announcement_id)
                
                # Keyingi yuborishgacha kutish (minutlarni sekundga o'tkazamiz)
                interval_seconds = announcement.interval * 60
                next_time = datetime.now() + timedelta(minutes=announcement.interval)
                print(f"⏰ Keyingi yuborish vaqti: {next_time.strftime('%H:%M:%S')}")
                print(f"⌛️ {announcement.interval} daqiqa kutilmoqda...")
                time.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in announcement thread: {str(e)}")
                time.sleep(RETRY_DELAY)

    thread = threading.Thread(target=run_thread, daemon=True)
    thread.start()
    return thread

# Server to'xtaganda clientni to'xtatish
import atexit
@atexit.register
def stop_client():
    try:
        client.stop()
    except:
        pass

def send_message_with_retry(bot, chat_id, message, retry_count=0):
    """Xabarni yuborish va xatolik bo'lsa qayta urinish"""
    try:
        return bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
    except RetryAfter as e:
        # Telegram cheklov qo'ygan, kutish kerak
        logger.warning(f"Rate limit exceeded. Waiting {e.retry_after} seconds")
        time.sleep(e.retry_after)
        return send_message_with_retry(bot, chat_id, message, retry_count)
    except TimedOut:
        # Timeout xatoligi, qayta urinish
        if retry_count < MAX_RETRIES:
            logger.warning(f"Timeout error. Retrying in {RETRY_DELAY} seconds. Attempt {retry_count + 1}/{MAX_RETRIES}")
            time.sleep(RETRY_DELAY)
            return send_message_with_retry(bot, chat_id, message, retry_count + 1)
        else:
            raise
    except TelegramError as e:
        # Boshqa Telegram xatoliklari
        if retry_count < MAX_RETRIES:
            logger.error(f"Telegram error: {str(e)}. Retrying in {RETRY_DELAY} seconds. Attempt {retry_count + 1}/{MAX_RETRIES}")
            time.sleep(RETRY_DELAY)
            return send_message_with_retry(bot, chat_id, message, retry_count + 1)
        else:
            raise
