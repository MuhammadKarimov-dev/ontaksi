from django.contrib import admin
from .models import Announcement, TelegramChannel

@admin.register(TelegramChannel)
class TelegramChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel_id', 'created_at', 'is_active')
    list_filter = ('is_active', 'type')
    search_fields = ('name', 'channel_id')
    ordering = ('-created_at',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('message', 'interval', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('message',)
    ordering = ('-created_at',)

