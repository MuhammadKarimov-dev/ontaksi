from pyrogram import Client, filters
import logging
from django.conf import settings
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import random
import os
import time
import signal
import psutil
import requests
from django.utils import timezone
from .models import VerificationCode
import asyncio

logger = logging.getLogger(__name__)

def wait_with_progress(total_seconds):
    """Kutish jarayonini progress bilan ko'rsatish"""
    for remaining in range(total_seconds, 0, -10):
        print(f"⏳ Kutilmoqda: {remaining} sekund qoldi...")
        time.sleep(10)

def send_sms(phone, message):
    """SMS yuborish"""
    try:
        # Eskiz SMS API
        url = "https://notify.eskiz.uz/api/message/sms/send"
        
        # Token olish
        auth_url = "https://notify.eskiz.uz/api/auth/login"
        auth_data = {
            "email": settings.SMS_EMAIL,
            "password": settings.SMS_PASSWORD
        }
        auth_response = requests.post(auth_url, json=auth_data)
        token = auth_response.json()['data']['token']
        
        # SMS yuborish
        headers = {
            "Authorization": f"Bearer {token}"
        }
        data = {
            "mobile_phone": phone.replace("+", ""),
            "message": message,
            "from": "4546"
        }
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"SMS yuborishda xatolik: {str(e)}")
        return False

class TelegramBot:
    _instance = None
    _is_running = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelegramBot, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            if not settings.TELEGRAM_BOT_TOKEN:
                raise ValueError("Bot tokeni topilmadi")

            self._is_running = False
            self.initialized = True
            self._setup_client()

    def _setup_client(self):
        """Pyrogram klientini sozlash"""
        try:
            self.client = Client(
                "taxi_bot",
                api_id=settings.TELEGRAM_API_ID,
                api_hash=settings.TELEGRAM_API_HASH,
                bot_token=settings.TELEGRAM_BOT_TOKEN,
                in_memory=True,
                parse_mode="html"
            )
            self._setup_handlers()
        except Exception as e:
            logger.error(f"Bot yaratishda xatolik: {str(e)}")
            raise

    def _setup_handlers(self):
        """Bot xabarlar uchun handlerlarni sozlash"""
        @self.client.on_message(filters.command("start"))
        def start_command(_, message):
            try:
                keyboard = ReplyKeyboardMarkup([
                    [KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]
                ], resize_keyboard=True)

                message.reply_text(
                    "Assalomu alaykum! 👋\n\n"
                    "Ro'yxatdan o'tish uchun telefon raqamingizni yuboring.\n"
                    "Tasdiqlash kodi SMS orqali yuboriladi.",
                    reply_markup=keyboard
                )
                print(f"✉️ Start: {message.from_user.id}")
            except Exception as e:
                logger.error(f"Start xatoligi: {str(e)}")

        @self.client.on_message(filters.contact)
        def handle_contact(_, message):
            try:
                phone = message.contact.phone_number
                user_id = message.from_user.id
                verification_code = str(random.randint(100000, 999999))

                # Eski kodni o'chirish
                VerificationCode.objects.filter(user_id=user_id).delete()
                
                # Yangi kodni saqlash
                VerificationCode.objects.create(
                    user_id=user_id,
                    code=verification_code,
                    phone=phone,
                    attempts=0
                )

                # SMS yuborish
                sms_text = f"Taxi Bot tasdiqlash kodingiz: {verification_code}"
                if send_sms(phone, sms_text):
                    message.reply_text(
                        f"✅ Telefon raqamingiz qabul qilindi: {phone}\n\n"
                        "📲 Tasdiqlash kodi SMS orqali yuborildi.\n"
                        "Iltimos, kodni kiriting.",
                        reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True)
                    )
                else:
                    # SMS yuborilmasa, Telegram orqali yuborish
                    message.reply_text(
                        f"✅ Telefon raqamingiz qabul qilindi: {phone}\n\n"
                        f"📝 Tasdiqlash kodingiz: {verification_code}",
                        reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True)
                    )
                print(f"📱 Foydalanuvchi: {phone}, kod: {verification_code}")
            except Exception as e:
                logger.error(f"Kontakt xatoligi: {str(e)}")
                message.reply_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

        @self.client.on_message(filters.text & ~filters.command("start"))
        def verify_code(_, message):
            try:
                user_id = message.from_user.id
                entered_code = message.text.strip()

                try:
                    verification = VerificationCode.objects.get(user_id=user_id)
                    if verification.is_expired():
                        verification.delete()
                        message.reply_text(
                            "⌛️ Tasdiqlash kodi eskirgan.\n"
                            "Iltimos, /start buyrug'ini qayta yuboring."
                        )
                        return
                except VerificationCode.DoesNotExist:
                    message.reply_text(
                        "❌ Avval telefon raqamingizni yuboring.\n"
                        "Buning uchun /start buyrug'ini yuboring."
                    )
                    return

                if verification.attempts >= 3:
                    message.reply_text(
                        "❌ Juda ko'p noto'g'ri urinish.\n"
                        "Qayta ro'yxatdan o'tish uchun /start buyrug'ini yuboring."
                    )
                    verification.delete()
                    return

                if entered_code == verification.code:
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("📞 Admin bilan bog'lanish", url="https://t.me/admin")]
                    ])
                    message.reply_text(
                        "✅ Kod to'g'ri tasdiqlandi!\n\n"
                        "👨‍💼 Admin bilan bog'lanish uchun quyidagi tugmani bosing:",
                        reply_markup=keyboard
                    )
                    print(f"✅ Tasdiq: {user_id}")
                    verification.delete()
                else:
                    verification.attempts += 1
                    verification.save()
                    remaining = 3 - verification.attempts
                    message.reply_text(
                        f"❌ Noto'g'ri kod. {remaining} ta urinish qoldi.\n"
                        "Iltimos, qayta urinib ko'ring."
                    )
            except Exception as e:
                logger.error(f"Tekshirish xatoligi: {str(e)}")
                message.reply_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

    def start(self):
        """Botni ishga tushirish"""
        if self._is_running:
            print("⚠️ Bot allaqachon ishlamoqda")
            return

        try:
            print("🚀 Bot ishga tushirilmoqda...")
            self.client.start()
            self._is_running = True
            print("✅ Bot muvaffaqiyatli ishga tushdi!")
            self.client.idle()
        except Exception as e:
            self._is_running = False
            if "FLOOD_WAIT_" in str(e):
                wait_time = int(str(e).split("FLOOD_WAIT_")[1].split("]")[0])
                print(f"⏳ Telegram cheklov qo'ydi. {wait_time} sekund kutish kerak...")
                time.sleep(wait_time)
                self.start()
            else:
                logger.error(f"Bot ishga tushirish xatoligi: {str(e)}")
                raise

    def stop(self):
        """Botni to'xtatish"""
        if self._is_running:
            self.client.stop()
            self._is_running = False
            print("🛑 Bot to'xtatildi")

    async def send_message(self, chat_id, text):
        """Foydalanuvchiga xabar yuborish"""
        try:
            await self.client.send_message(chat_id, text)
            return True
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik: {str(e)}")
            return False

    def send_message_to_channel(self, message):
        """Kanalga xabar yuborish"""
        try:
            # Yangi client yaratish
            app = Client(
                "taxi_bot_temp",
                api_id=settings.TELEGRAM_API_ID,
                api_hash=settings.TELEGRAM_API_HASH,
                bot_token=settings.TELEGRAM_BOT_TOKEN,
                in_memory=True
            )
            
            # Start qilish va xabar yuborish
            app.start()
            try:
                # Kanal ID @ bilan boshlansa
                if str(settings.TELEGRAM_CHANNEL_ID).startswith('@'):
                    channel_id = settings.TELEGRAM_CHANNEL_ID
                else:
                    # Raqamli ID bo'lsa
                    channel_id = int(settings.TELEGRAM_CHANNEL_ID)
                    
                app.send_message(
                    chat_id=channel_id,
                    text=message,
                    parse_mode="html"
                )
                return True
            finally:
                app.stop()
            
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik: {str(e)}")
            return False