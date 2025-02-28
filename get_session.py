from pyrogram import Client

API_ID = '27075572'
API_HASH = '1b56557db16cca997768fe87a724e75b'

app = Client(
    "my_account", 
    api_id=API_ID, 
    api_hash=API_HASH,
    no_updates=True
)

with app:
    session_string = app.export_session_string()
    print("\nSIZNING SESSION STRINGIZ:")
    print("------------------------")
    print(session_string)
    print("------------------------")
    print("\nBu string ni announcement_sender.py faylidagi SESSION_STRING o'zgaruvchisiga qo'ying") 