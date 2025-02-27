from pyrogram import Client
import os
import logging

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
        self._started = False
        
    def _ensure_started(self):
        if not self._started:
            try:
                self.app.start()
                self._started = True
                logger.info("Bot started successfully")
            except Exception as e:
                logger.error(f"Start error: {str(e)}")
                raise e
    
    def send_message_sync(self, chat_id, text):
        try:
            self._ensure_started()
            logger.info(f"Sending message to {chat_id}: {text}")
            
            # Agar chat_id @ bilan boshlansa, uni olib tashlaymiz
            if isinstance(chat_id, str) and chat_id.startswith('@'):
                chat_id = chat_id[1:]
                
            self.app.send_message(chat_id, text)
            logger.info("Message sent successfully")
            return True
        except Exception as e:
            logger.error(f"Send message error: {str(e)}")
            return False