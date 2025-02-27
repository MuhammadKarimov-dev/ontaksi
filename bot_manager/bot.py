from pyrogram import Client
import os
import logging

logger = logging.getLogger(__name__)

class TelegramBot:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelegramBot, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        session_path = "/var/www/ontaksi/sessions"
        if not os.path.exists(session_path):
            os.makedirs(session_path)
            
        self.app = Client(
            f"{session_path}/user_taxi",
            api_id=27075572,
            api_hash="1b56557db16cca997768fe87a724e75b",
            no_updates=True
        )
        self.app.start()
        self._initialized = True
        logger.info("Bot initialized and started")
    
    def send_message_sync(self, chat_id, text):
        try:
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