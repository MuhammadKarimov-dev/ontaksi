from django.contrib import admin
from .models import Announcement, TelegramChannel

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'time', 'member', 'women', 'phone')
    list_filter = ('address', 'women', 'time')
    search_fields = ('user__username', 'phone')

@admin.register(TelegramChannel)
class TelegramChannelAdmin(admin.ModelAdmin):
    list_display = ('channel_name', 'channel_id', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('channel_name', 'channel_id')
