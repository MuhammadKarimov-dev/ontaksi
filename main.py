from pyrogram import Client

api_id='27075572'
api_hash='1b56557db16cca997768fe87a724e75b'

app = Client("user_taxi", api_id, api_hash)

with app:
    chats = app.get_dialogs()
    for chat in chats:
        print(f"{chat.chat.title} - {chat.chat.id}")
