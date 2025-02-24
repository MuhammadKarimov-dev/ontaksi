import asyncio
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from .models import Announcement, TelegramChannel,ActiveTask
from bot_manager.telegram_bot import TelegramBot
from django.contrib import messages 

from django.conf import settings
from django.core.management import call_command
import threading


def home(request):
    announcements = Announcement.objects.all().order_by('-id')[:10]
    return render(request, 'announcement/home.html', {'announcements': announcements})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        return render(request, 'auth/login.html', {'error': 'Login yoki parol xato!'})
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def start_announcement(request, announcement_id):
    announcement = Announcement.objects.get(id=announcement_id)
    active_channels = TelegramChannel.objects.filter(is_active=True)
    
    if active_channels.count() == 0:
        messages.error(request, 'Фаол каналлар топилмади!')
        return redirect('channel_list')
    
    # Create ActiveTask
    ActiveTask.objects.create(
        announcement_id=announcement_id,
        is_active=True
    )
    
    # Start sending in background
    thread = threading.Thread(
        target=call_command,
        args=('announcement_sender', 'start', announcement_id),
        daemon=True
    )
    thread.start()
    
    messages.success(request, 'Эълон юбориш бошланди!')
    return redirect('announcement_list')

@login_required
def stop_announcement(request, announcement_id):
    # Stop the task
    ActiveTask.objects.filter(
        announcement_id=announcement_id,
        is_active=True
    ).update(is_active=False)
    
    messages.info(request, 'Эълон юбориш тўхтатилди!')
    return redirect('announcement_list')

@login_required
def delete_announcement(request, announcement_id):
    announcement = Announcement.objects.get(id=announcement_id)
    if announcement.user == request.user:
        ActiveTask.objects.filter(announcement_id=announcement_id).delete()
        announcement.delete()
    return redirect('announcement_list')

@login_required
def create_announcement(request):
    if request.method == 'POST':
        Announcement.objects.create(
            user=request.user,
            message=request.POST.get('message'),
            interval=int(request.POST.get('interval', 5))
        )
        return redirect('announcement_list')
    return render(request, 'announcement/create.html')

@login_required
def edit_announcement(request, announcement_id):
    announcement = Announcement.objects.get(id=announcement_id)
    
    if request.method == 'POST':
        if announcement.user == request.user:
            announcement.message = request.POST.get('message')
            announcement.interval = int(request.POST.get('interval', 5))
            announcement.save()
            
            ActiveTask.objects.filter(announcement_id=announcement_id).delete()
            messages.info(request, 'Эълон таҳрирланди. Қайта ишга тушириш учун "Бошлаш" тугмасини босинг.')
            return redirect('announcement_list')
    context = {'announcement': announcement}
    return render(request, 'announcement/edit.html', context)

@login_required
def announcement_list(request):
    announcements = Announcement.objects.filter(user=request.user).order_by('id')
    active_tasks = ActiveTask.objects.filter(
        is_active=True
    ).values_list('announcement_id', flat=True)
    
    context = {
        'announcements': announcements,
        'active_announcements': list(active_tasks)
    }
    return render(request, 'announcement/list.html', context)

@login_required
def channel_list(request):
    channels = TelegramChannel.objects.all()
    return render(request, 'announcement/channels.html', {'channels': channels})

@login_required
def add_channel(request):
    if request.method == 'POST':
        channel_id = request.POST.get('channel_id').strip()
        name = request.POST.get('name')
        if channel_id.startswith('http'):
            channel_id = channel_id.split('/')[-1]
        if channel_id.startswith('@'):
            channel_id = channel_id[1:]
        if channel_id.replace('-', '').isdigit() and not channel_id.startswith('-'):
            channel_id = f"-{channel_id}"

        # Check if channel already exists
        if TelegramChannel.objects.filter(channel_id=channel_id).exists():
            messages.error(request, 'Бу канал аллақачон мавжуд!')
            return redirect('channel_list')

        TelegramChannel.objects.create(
            channel_id=channel_id,
            channel_name=name,
            is_active=True
        )
        messages.success(request, 'Канал муваффақиятли қўшилди!')
        return redirect('channel_list')
    return render(request, 'announcement/add_channel.html')

@login_required
def toggle_channel(request, channel_id):
    channel = TelegramChannel.objects.get(id=channel_id)
    channel.is_active = not channel.is_active
    channel.save()
    return redirect('channel_list')

@login_required
def delete_channel(request, channel_id):
    channel = TelegramChannel.objects.get(id=channel_id)
    channel.delete()
    return redirect('channel_list')
