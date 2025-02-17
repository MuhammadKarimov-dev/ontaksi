from django.conf import settings

def admin_contacts(request):
    return {
        'ADMIN_PHONE': getattr(settings, 'ADMIN_PHONE', '+998 XX XXX XX XX'),
        'ADMIN_TELEGRAM': getattr(settings, 'ADMIN_TELEGRAM', 'X'),
    }