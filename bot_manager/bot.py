from pyrogram import Client

class TelegramBot:
    def __init__(self):
        self.app = Client(
            "user_taxi",
            api_id=24351440,
            api_hash="8601d1a62d0703c6194c4b3f14d3e9fe",
            no_updates=True,    # vergul to'g'ri
            in_memory=True      # oxirgi qatorda vergul bo'lmasligi kerak
        )
        
    async def start(self):
        try:
            await self.app.start()
        except Exception as e:
            print(f"Start error: {str(e)}")
        
    async def stop(self):
        try:
            if self.app:
                await self.app.stop()
        except Exception as e:
            print(f"Stop error: {str(e)}")
        
    async def send_message(self, chat_id, text):
        try:
            if self.app and self.app.is_connected:
                await self.app.send_message(chat_id, text)
        except Exception as e:
            print(f"Send message error: {str(e)}")