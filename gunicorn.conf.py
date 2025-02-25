# Gunicorn configuration
workers = 3  # CPU cores * 2 + 1
worker_class = 'sync'  # Django uchun sync worker yaxshi ishlaydi
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

def on_starting(server):
    # Bot ni ishga tushirish
    from bot_manager.bot import TelegramBot
    TelegramBot() 