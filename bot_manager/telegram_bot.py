from pyrogram import Client
import asyncio
try:
    from bot_manager.bot_config import api_id, api_hash
except :
    from bot_config import api_id, api_hash

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
            print(f"Xabar yuborishda xatolik: {e}")
            return False

    def send_message_sync(self, channel_id, message):
        """Sinxron xabar yuborish"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.send_message(channel_id, message))
        finally:
            loop.close()

# t=TelegramBot()
# asyncio.run(t.send_message(-1002438647274, 'salom'))
