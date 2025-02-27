from pyrogram import Client
import os
import logging
import asyncio

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        session_path = "/var/www/ontaksi/sessions"
        if not os.path.exists(session_path):
            os.makedirs(session_path)
            
        self.app = Client(
            f"{session_path}/user_taxi",
            api_id=27075572,
            api_hash="1b56557db16cca997768fe87a724e75b",
            no_updates=True
        )
        logger.info("Bot initialized")

    async def send_message_async(self, chat_id, text):
        """Asinxron xabar yuborish"""
        async with self.app:
            if isinstance(chat_id, str) and chat_id.startswith('@'):
                chat_id = chat_id[1:]
            await self.app.send_message(chat_id, text)

    def send_message_sync(self, chat_id, text):
        """Sinxron xabar yuborish"""
        try:
            logger.info(f"Sending message to {chat_id}")
            asyncio.run(self.send_message_async(chat_id, text))
            logger.info("Message sent successfully")
            return True
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik: {str(e)}")
            return False