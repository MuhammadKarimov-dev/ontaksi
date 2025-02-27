from pathlib import Path
from dotenv import load_dotenv
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-@i)!+(41weo9jc21w&r3959^0$d)bytq4+8_r40!-7b2jh0$wj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['81.200.146.99', 'ontaksi.uz', 'localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'announcement.apps.AnnouncementConfig',
    'bot_manager.apps.BotManagerConfig',
    'users',  # mavjud bo'lsa
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'taxi_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = "TaxiSayt.asgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = [
    "https://*",  # Barcha HTTPS domenlar uchun
    "http://*",    # Ngrok domeningizni shu yerga qo'shing
    'https://*.ngrok-free.app',
    'http://81.200.146.99',  # Yangi IP qo'shildi
    'http://ontaksi.uz',    # Yangi domen qo'shildi
]

STATIC_URL = '/static/'  # Static URL yo'li

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # Static fayllar joylashgan papka
]

# Static fayllarni yig'ish uchun
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  



LOGIN_URL = 'login'  # login_view funksiyasining name'i
LOGIN_REDIRECT_URL = 'dashboard' 

# Thread va Memory settings
MAX_WORKER_THREADS = 10
MAX_MEMORY_PERCENT = 80
MONITORING_INTERVAL = 60  # seconds

# Alert thresholds
MEMORY_ALERT_THRESHOLD = 85  # percentage
ERROR_ALERT_THRESHOLD = 10  # errors per minute

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',  # Faqat xatoliklarni yozish
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'ERROR',  # Faqat xatoliklarni yozish
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
} 

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

SECURE_CROSS_ORIGIN_OPENER_POLICY = None 

AUTH_USER_MODEL = 'announcement.CustomUser' 

# Telegram API sozlamalari
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') 

# SMS sozlamalari
SMS_API_URL = os.getenv('SMS_API_URL', 'https://api.sms.provider.com/send')
SMS_API_KEY = os.getenv('SMS_API_KEY') 

# Eskiz.uz sozlamalari
ESKIZ_EMAIL = os.getenv('ESKIZ_EMAIL')
ESKIZ_PASSWORD = os.getenv('ESKIZ_PASSWORD') 

# Telegram kanal ID
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID') 