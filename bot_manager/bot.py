from pyrogram import Client
import os
import logging

logger = logging.getLogger(__name__)

class TelegramBot:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            print("Creating new TelegramBot instance")
            cls._instance = super(TelegramBot, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        print("Initializing TelegramBot")
        session_path = "/var/www/ontaksi/sessions"
        if not os.path.exists(session_path):
            os.makedirs(session_path)
            
        try:
            print("Creating Pyrogram client")
            self.app = Client(
                f"{session_path}/user_taxi",
                api_id=27075572,
                api_hash="1b56557db16cca997768fe87a724e75b",
                no_updates=True
            )
            print("Starting Pyrogram client")
            self.app.start()
            print("Pyrogram client started successfully")
            self._initialized = True
        except Exception as e:
            print(f"Error initializing bot: {str(e)}")
            raise e
    
    def send_message_sync(self, chat_id, text):
        try:
            print(f"Attempting to send message to {chat_id}")
            
            # Agar chat_id @ bilan boshlansa, uni olib tashlaymiz
            if isinstance(chat_id, str) and chat_id.startswith('@'):
                chat_id = chat_id[1:]
                print(f"Modified chat_id: {chat_id}")
            
            # Xabar yuborish
            print("Sending message...")
            self.app.send_message(chat_id, text)
            print("Message sent successfully")
            return True
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False