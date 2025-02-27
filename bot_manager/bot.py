from pyrogram import Client

class TelegramBot:
    def __init__(self):
        self.app = Client(
            "user_taxi",
            api_id=27075572,      # API ID ni kiriting
            api_hash="1b56557db16cca997768fe87a724e75b"  # API HASH ni kiriting
        )
        
    async def start(self):
        pass  # Bot funksionalligini o'chirish

    async def stop(self):
        pass  # Bot funksionalligini o'chirish

    async def send_message(self, chat_id, text):
        try:
            await self.app.send_message(chat_id, text)
        except Exception as e:
            print(f"Send message error: {str(e)}")