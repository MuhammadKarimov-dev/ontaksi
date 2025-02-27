from pyrogram import Client
import asyncio
import logging
import traceback

try:
    from bot_manager.bot_config import api_id, api_hash
except:
    from bot_config import api_id, api_hash

# Logging ni sozlash
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class TelegramBot:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._app = Client(
                "user_taxi",
                api_id=api_id,
                api_hash=api_hash,
                no_updates=True
            )
            self._initialized = True
            self._is_connected = False
            self._lock = asyncio.Lock()
            # Har bir instance uchun yangi event loop yaratish
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

    def __del__(self):
        """Event loopni to'g'ri yopish"""
        if hasattr(self, '_loop') and self._loop.is_running():
            self._loop.run_until_complete(self.disconnect())
            self._loop.close()

    async def connect(self):
        """Telegram klientini ulash"""
        async with self._lock:
            if not self._is_connected:
                await self._app.start()
                self._is_connected = True

    async def disconnect(self):
        """Telegram klientini uzish"""
        async with self._lock:
            if self._is_connected:
                await self._app.stop()
                self._is_connected = False

    async def send_message(self, channel_id, message):
        """Xabar yuborish"""
        try:
            if not self._is_connected:
                await self.connect()
            await self._app.send_message(channel_id, message)
            return True
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik: {e}")
            logger.debug(traceback.format_exc())
            return False

    def send_message_sync(self, channel_id, message):
        """Sinxron xabar yuborish"""
        try:
            return self._loop.run_until_complete(self.send_message(channel_id, message))
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik: {e}")
            logger.debug(traceback.format_exc())
            return False

# t=TelegramBot()
# asyncio.run(t.send_message(-1002438647274, 'salom'))
