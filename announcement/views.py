from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from .models import Announcement, TelegramChannel, CustomUser, Message, SMSVerification, Channel
from django.contrib import messages 
import threading
from announcement.announcement_sender import send_messages
from bot_manager.bot import TelegramBot
import logging
from .forms import CustomUserCreationForm, MessageForm
from sms_manager.sms_service import send_sms
import time
import json
from django.http import JsonResponse
import random
import string

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
        message = request.POST.get('message')
        interval = int(request.POST.get('interval'))
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        channel_ids = request.POST.getlist('channels')
        
        # E'lon yaratish
        announcement = Announcement.objects.create(
            user=request.user,
            message=message,
            interval=interval,
            start_time=start_time,
            end_time=end_time
        )
        
        # Kanallarni qo'shish
        channels = Channel.objects.filter(id__in=channel_ids, user=request.user)
        announcement.channels.add(*channels)
        
        messages.success(request, "E'lon muvaffaqiyatli yaratildi!")
        return redirect('dashboard')
        
    context = {
        'channels': Channel.objects.filter(user=request.user, is_active=True)
    }
    return render(request, 'announcement/create_announcement.html', context)

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
        channel_username = request.POST.get('username').strip()
        channel_name = request.POST.get('name')
        
        # @ belgisini olib tashlash
        if channel_username.startswith('@'):
            channel_username = channel_username[1:]
            
        # Kanal mavjudligini tekshirish
        if Channel.objects.filter(channel_username=channel_username, user=request.user).exists():
            messages.error(request, "Bu kanal allaqachon qo'shilgan!")
            return redirect('channel_list')
            
        Channel.objects.create(
            user=request.user,
            channel_username=channel_username,
            channel_name=channel_name,
            is_active=True
        )
        messages.success(request, "Kanal muvaffaqiyatli qo'shildi!")
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

def is_superuser(user):
    return user.is_superuser

@login_required
def dashboard(request):
    if request.user.is_superuser:
        users = CustomUser.objects.all()
        return render(request, 'announcement/admin_dashboard.html', {
            'users': users,
        })
    else:
        return render(request, 'announcement/user_dashboard.html')

@login_required
def verify_user(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, "Sizda bunday huquq yo'q!")
        return redirect('dashboard')
    
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_verified = True
    user.save()
    
    messages.success(request, f"{user.username} tasdiqlandi!")
    return redirect('dashboard')

@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, "Sizda bunday huquq yo'q!")
        return redirect('dashboard')
    
    user = get_object_or_404(CustomUser, id=user_id)
    if user.is_superuser:
        messages.error(request, "Super foydalanuvchini o'chirib bo'lmaydi!")
        return redirect('dashboard')
        
    user.delete()
    messages.success(request, "Foydalanuvchi o'chirildi!")
    return redirect('dashboard')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Muvaffaqiyatli ro'yxatdan o'tdingiz!")
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'announcement/register.html', {'form': form})

@login_required
def send_message(request):
    if not request.user.is_staff:
        messages.error(request, "Sizda bunday huquq yo'q!")
        return redirect('dashboard')
        
    if request.method == 'POST':
        message_text = request.POST.get('message')
        interval = int(request.POST.get('interval', 3))
        users = CustomUser.objects.filter(is_verified=True)
        bot = TelegramBot()
        
        success_count = 0
        error_count = 0
        
        for user in users:
            try:
                # Xabarni saqlash
                message = Message.objects.create(
                    user=user,
                    text=message_text
                )
                
                # Telegram orqali yuborish
                if user.telegram_id:
                    if bot.send_message(user.telegram_id, message_text):
                        message.sent_via_telegram = True
                        success_count += 1
                
                # SMS orqali yuborish
                if user.phone_number:
                    if send_sms(user.phone_number, message_text):
                        message.sent_via_sms = True
                        success_count += 1
                
                message.save()
                time.sleep(interval)
                
            except Exception as e:
                error_count += 1
                print(f"Xatolik: {str(e)}")
        
        messages.success(request, f"Xabar {success_count} ta foydalanuvchiga yuborildi. {error_count} ta xatolik yuz berdi.")
        return redirect('dashboard')
    
    return render(request, 'announcement/send_message.html')

def generate_password():
    """8 ta belgidan iborat tasodifiy parol yaratish"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(8))

@login_required
def add_user(request):
    if not request.user.is_superuser:
        messages.error(request, "Sizda bunday huquq yo'q!")
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        try:
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                phone_number=phone,
                is_verified=True
            )
            messages.success(request, "Foydalanuvchi muvaffaqiyatli qo'shildi!")
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
    
    context = {
        'generated_password': generate_password()
    }
    return render(request, 'announcement/add_user.html', context)

@login_required
def send_verification_sms(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': "Sizda bunday huquq yo'q!"})
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            message = f"OnTaxi tizimiga yangi foydalanuvchi qo'shildi!\n\n👤 Login: {username}\n🔑 Parol: {password}"
            
            # Telegram orqali yuborish
            bot = TelegramBot()
            if bot.send_message_to_channel(message):
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Xabar yuborishda xatolik'})
                
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Noto\'g\'ri so\'rov'})
