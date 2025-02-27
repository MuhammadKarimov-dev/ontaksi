from pyrogram import Client

class TelegramBot:
    def __init__(self):
        self.app = Client(
            "user_taxi",
            api_id=24351440,
            api_hash="8601d1a62d0703c6194c4b3f14d3e9fe",
            no_updates=True,
            in_memory=True
        )
        self._started = False
        
    async def start(self):
        if not self._started:
            try:
                await self.app.start()
                self._started = True
            except Exception as e:
                print(f"Start error: {str(e)}")
        
    async def stop(self):
        if self._started:
            try:
                await self.app.stop()
                self._started = False
            except Exception as e:
                print(f"Stop error: {str(e)}")
        
    async def send_message(self, chat_id, text):
        if not self._started:
            await self.start()
        try:
            await self.app.send_message(chat_id, text)
        except Exception as e:
            print(f"Send message error: {str(e)}")