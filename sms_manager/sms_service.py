import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def get_eskiz_token():
    """Eskiz.uz dan token olish"""
    try:
        url = "https://notify.eskiz.uz/api/auth/login"
        
        data = {
            'email': settings.ESKIZ_EMAIL,
            'password': settings.ESKIZ_PASSWORD
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('token')
            
        logger.error(f"Token olishda xatolik: {response.text}")
        return None
            
    except Exception as e:
        logger.error(f"Token olishda xatolik: {str(e)}")
        return None

def send_sms(phone_number, message):
    """SMS yuborish funksiyasi"""
    try:
        token = get_eskiz_token()
        if not token:
            return False
            
        url = "https://notify.eskiz.uz/api/message/sms/send"
        
        # +998 ni olib tashlash
        phone = phone_number.replace('+', '')
        
        payload = {
            'mobile_phone': phone,
            'message': message,
            'from': '4546'
        }
        
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                logger.info(f"SMS yuborildi: {phone_number}")
                return True
                
        logger.error(f"SMS yuborishda xatolik: {response.text}")
        return False
            
    except Exception as e:
        logger.error(f"SMS yuborishda xatolik: {str(e)}")
        return False 