from django.contrib import admin
from .models import Announcement, TelegramChannel

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_preview', 'interval', 'is_active')
    list_filter = ('user', 'interval')
    search_fields = ('user__username', 'message')

    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'

@admin.register(TelegramChannel)
class TelegramChannelAdmin(admin.ModelAdmin):
    list_display = ('channel_name', 'channel_id', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('channel_name', 'channel_id')

