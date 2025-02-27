from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from .models import Announcement, TelegramChannel
from django.contrib import messages 
import threading
from announcement.announcement_sender import send_messages
from bot_manager.telegram_bot import TelegramBot
import logging

logger = logging.getLogger(__name__)

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
    try:
        announcement = get_object_or_404(Announcement, id=announcement_id)
        if announcement.user == request.user:
            announcement.is_active = True
            announcement.save()
            
            thread = threading.Thread(target=send_messages, args=(announcement_id,), daemon=True)
            thread.start()
            
            messages.success(request, "E'lon yuborish boshlandi")
        else:
            messages.error(request, "Sizda bunday huquq yo'q!")
            
    except Exception as e:
        logger.error(f"Start announcement error: {str(e)}")
        messages.error(request, "Xatolik yuz berdi")
    
    return redirect("announcement_list")

@login_required
def stop_announcement(request, announcement_id):
    try:
        announcement = get_object_or_404(Announcement, id=announcement_id)
        announcement.is_active = False
        announcement.save()
        messages.info(request, "E'lon to'xtatildi")
    except Exception as e:
        messages.error(request, "Xatolik yuz berdi")
    return redirect("announcement_list")

@login_required
def delete_announcement(request, announcement_id):
    announcement = Announcement.objects.get(id=announcement_id)
    if announcement.user == request.user:
        announcement.delete()
    return redirect('announcement_list')

@login_required
def create_announcement(request):
    if request.method == 'POST':
        try:
            message = request.POST.get('message')
            interval = int(request.POST.get('interval', 5))
            
            # Faqat e'lonni yaratamiz, yubormaymiz
            announcement = Announcement.objects.create(
                user=request.user,
                message=message,
                interval=interval,
                is_active=False  # Boshlash tugmasi bosilmaguncha faol emas
            )

            messages.success(request, "E'lon muvaffaqiyatli yaratildi. Yuborishni boshlash uchun 'Boshlash' tugmasini bosing.")
            return redirect('announcement_list')

        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {e}")
            return redirect('create_announcement')

    return render(request, 'announcement/create.html')

@login_required
def edit_announcement(request, announcement_id):
    announcement = Announcement.objects.get(id=announcement_id)
    
    if request.method == 'POST':
        if announcement.user == request.user:
            announcement.message = request.POST.get('message')
            announcement.interval = int(request.POST.get('interval', 5))
            announcement.save()
        
            messages.info(request, 'Эълон таҳрирланди. Қайта ишга тушириш учун "Бошлаш" тугмасини босинг.')
            return redirect('announcement_list')
    context = {'announcement': announcement}
    return render(request, 'announcement/edit.html', context)

@login_required
def announcement_list(request):
    announcements = Announcement.objects.filter(user=request.user).order_by('id')
    context = {
        'announcements': announcements,
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
