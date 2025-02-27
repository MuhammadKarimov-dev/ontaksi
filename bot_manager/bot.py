from pyrogram import Client
import asyncio
import os

class TelegramBot:
    def __init__(self):
        session_path = "/var/www/ontaksi/sessions"
        if not os.path.exists(session_path):
            os.makedirs(session_path)
            
        self.app = Client(
            f"{session_path}/user_taxi",
            api_id=27075572,  # Yangi API ID
            api_hash="1b56557db16cca997768fe87a724e75b",  # Yangi API HASH
            no_updates=True
        )
        self._started = False
        
    def _ensure_started(self):
        if not self._started:
            try:
                self.app.start()
                self._started = True
                print("Bot started successfully")
            except Exception as e:
                print(f"Start error: {str(e)}")
                raise e
    
    def send_message_sync(self, chat_id, text):
        try:
            self._ensure_started()
            print(f"Sending message to {chat_id}: {text}")
            self.app.send_message(chat_id, text)
            print("Message sent successfully")
            return True
        except Exception as e:
            print(f"Send message error: {str(e)}")
            return False