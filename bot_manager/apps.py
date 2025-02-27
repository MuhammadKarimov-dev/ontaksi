from django.apps import AppConfig

class BotManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot_manager'
    label = 'bot_manager'
    verbose_name = 'Bot Manager'

    def ready(self):
        """Ilova ishga tushganda bajariladigan kod"""
        pass 