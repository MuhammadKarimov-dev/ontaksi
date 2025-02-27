from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, SMSCode

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('phone', 'first_name', 'last_name', 'is_staff')
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Shaxsiy maʼlumotlar', {'fields': ('first_name', 'last_name', 'telegram_id')}),
        ('Ruxsatlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Muhim sanalar', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2'),
        }),
    )
    ordering = ('phone',)

@admin.register(SMSCode)
class SMSCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'is_used')
    list_filter = ('is_used',) 