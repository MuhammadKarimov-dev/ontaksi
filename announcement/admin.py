from django.contrib import admin
from .models import Announcement, TelegramChannel, PhoneNumber
from django.utils.html import format_html
from .announcement_sender import send_sms
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Message

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

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('number', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('number',)
    ordering = ('-created_at',)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'phone_number', 'telegram_id', 'is_verified', 'is_staff')
    list_filter = ('is_verified', 'is_staff')
    search_fields = ('username', 'phone_number', 'telegram_id')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Qo\'shimcha ma\'lumotlar', {
            'fields': ('phone_number', 'telegram_id', 'is_verified'),
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Qo\'shimcha ma\'lumotlar', {
            'fields': ('phone_number', 'telegram_id', 'is_verified'),
        }),
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'text_preview', 'sent_via_telegram', 'sent_via_sms', 'created_at')
    list_filter = ('sent_via_telegram', 'sent_via_sms')
    search_fields = ('text', 'user__username')
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Xabar matni'

# CustomUserAdmin ni olib tashlang

