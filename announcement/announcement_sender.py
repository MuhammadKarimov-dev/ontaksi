import threading
import time
import asyncio
from pyrogram import Client
from django.db import transaction
from asgiref.sync import sync_to_async
from .models import Announcement, TelegramChannel

# Telegram API credentials
API_ID = '27075572'
API_HASH = '1b56557db16cca997768fe87a724e75b'
SESSION_STRING = 'AgGdI_QAKOQSmLz6qF6ewBelgymYCmk76TXX4vBSQG3-oUYyxybu2tNykk__e9Fza5fIj1j-wI9HMqz-XFY7pHj82PPuYvocel2Ww9rOH8A_AhWWMfRHqN1ZhdlAbQUPV0jSDfxCvtjoplS4kImeHxFZ3I6obYCBOjHO_cOUXzHWBc6fhrRZvj4TiO47vsqd1a_dzl0m3Duni8DFZjvG9G3NjRw3RhBlREUYY7pcHkmkIZOOSJaRnAbVScRcpCNT5w4wKI5G5vo9g9zZnNrcwq6FKehA03DMvtk8cceLtCLD8xNyJeSqABAeZ4rpRVkIXEzRbweYLOzxbPx-H6aXuMqGQOy5MgAAAAANJISAAA'  # get_session.py dan olgan REAL session stringni qo'ying

async def send_message_async(app, channel, message):
    try:
        chat_id = channel.channel_id
        
        # String bo'lsa int ga o'tkazamiz
        if isinstance(chat_id, str) and not chat_id.startswith('@'):
            try:
                chat_id = int(chat_id)
            except:
                pass
                
        await app.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=None
        )
        print(f"✅ Xabar yuborildi: {channel.channel_id}")
    except Exception as e:
        print(f"❌ Xabar yuborilmadi: {channel.channel_id} - {str(e)}")
    await asyncio.sleep(1)

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

def run_async_in_thread(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

async def send_messages_async(announcement_id):
    get_announcement_async = sync_to_async(get_announcement)
    get_channels_async = sync_to_async(get_active_channels)
    
    while True:
        try:
            # Har safar yangi announcement ma'lumotlarini olamiz
            announcement = await get_announcement_async(announcement_id)

            if announcement is None or not announcement.is_active:
                print(f"⏹ E'lon to'xtatildi yoki o'chirildi: {announcement_id}")
                break

            app = Client(
                "my_account", 
                api_id=API_ID, 
                api_hash=API_HASH,
                session_string=SESSION_STRING,
                in_memory=True,
                no_updates=True
            )
            await app.start()

            try:
                channels = await get_channels_async()
                for channel in channels:
                    await send_message_async(app, channel, announcement.message)
            finally:
                await app.stop()

            # Har safar yangi interval qiymatini olamiz
            updated_announcement = await get_announcement_async(announcement_id)
            if updated_announcement:
                interval = updated_announcement.interval
            else:
                interval = 60  # Default interval
                
            print(f"⏰ Keyingi xabar {interval} daqiqadan so'ng yuboriladi")
            await asyncio.sleep(interval * 60)

        except Exception as e:
            print(f"❌ Xato: {e}")
            await asyncio.sleep(5)

def send_messages(announcement_id):
    """Berilgan e'lonni Telegramga yuborish"""
    run_async_in_thread(send_messages_async(announcement_id))

def start_announcement_thread(announcement):
    """E'lonni alohida thread'da ishga tushirish"""
    print(f"📝 E'lon yuborish boshlandi: {announcement.message[:30]}...")
    
    thread = threading.Thread(
        target=send_messages,
        args=(announcement.id,),
        daemon=True
    )
    thread.start()
    print("🔄 Thread boshlandi")

# Server to'xtaganda clientni to'xtatish
import atexit
@atexit.register
def stop_client():
    try:
        client.stop()
    except:
        pass
