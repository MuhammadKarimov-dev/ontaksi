from pyrogram import Client
import asyncio
import threading
from queue import Queue
import time

class TelegramBot:
    _instance = None
    _lock = threading.Lock()
    _message_queue = Queue()
    _event_loop = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            try:
                from bot_manager.bot_config import api_id, api_hash
            except:
                from bot_config import api_id, api_hash

            self._app = Client(
                "user_taxi",
                api_id=api_id,
                api_hash=api_hash,
                no_updates=True
            )
            self._is_connected = False
            self._initialized = True
            self._setup_event_loop()
            self._start_sender()

    def _setup_event_loop(self):
        """Event loop ni sozlash"""
        if self._event_loop is None:
            self._event_loop = asyncio.new_event_loop()
            thread = threading.Thread(target=self._run_event_loop, daemon=True)
            thread.start()

    def _run_event_loop(self):
        """Event loop ni ishga tushirish"""
        asyncio.set_event_loop(self._event_loop)
        self._event_loop.run_forever()

    def _start_sender(self):
        """Xabar yuboruvchi thread ni ishga tushirish"""
        def sender_worker():
            try:
                # Bot'ni ulash
                future = asyncio.run_coroutine_threadsafe(
                    self._connect(), 
                    self._event_loop
                )
                future.result()

                while True:
                    if not self._message_queue.empty():
                        chat_id, message = self._message_queue.get()
                        future = asyncio.run_coroutine_threadsafe(
                            self._send_message(chat_id, message),
                            self._event_loop
                        )
                        future.result()
                    time.sleep(1)

            except Exception as e:
                print(f"Sender worker xatolik: {str(e)}")

        self._sender_thread = threading.Thread(target=sender_worker, daemon=True)
        self._sender_thread.start()

    async def _connect(self):
        """Telegram klientini ulash"""
        if not self._is_connected:
            try:
                await self._app.start()
                self._is_connected = True
                print("Bot muvaffaqiyatli ulandi")
            except Exception as e:
                print(f"Ulanishda xatolik: {str(e)}")
                self._is_connected = False

    async def _send_message(self, chat_id, message):
        """Xabar yuborish"""
        try:
            if not self._is_connected:
                await self._connect()
            await self._app.send_message(chat_id, message)
            print(f"✅ Xabar yuborildi: {chat_id}")
            return True
        except Exception as e:
            print(f"Xabar yuborishda xatolik: {str(e)}")
            return False

    def send_message(self, chat_id, message):
        """Xabarni navbatga qo'shish"""
        self._message_queue.put((chat_id, message))

# t=TelegramBot()
# asyncio.run(t.send_message(-1002438647274, 'salom'))
