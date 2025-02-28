from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from .models import Announcement, TelegramChannel
from django.contrib import messages
from .announcement_sender import send_messages, start_announcement_thread
from django.http import JsonResponse
import threading
from django.db import connection
from django.db.utils import OperationalError
from django.db.transaction import atomic

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
            return redirect('announcement:list')
        else:
            return render(request, 'auth/login.html', {
                'error': 'Username yoki password xato!'
            })
    
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('announcement:list')

@login_required
def announcement_list(request):
    # Faqat birinchi e'lonni olish
    announcement = Announcement.objects.first()
    return render(request, 'announcement/list.html', {'announcement': announcement})

@login_required
def create_announcement(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        interval = request.POST.get('interval', 60)  # Default 60 sekund
        
        if message:
            announcement = Announcement.objects.create(
                user=request.user,
                message=message,
                interval=interval,
                is_active=False
            )
            messages.success(request, 'Хабар муваффақиятли яратилди!')
            return redirect('announcement:list')
        else:
            messages.error(request, 'Хабар матни киритилмаган!')
            
    return render(request, 'announcement/create.html')

@login_required
def edit_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    if request.method == 'POST':
        print("POST data:", request.POST)  # Debug
        
        message = request.POST.get('message')
        interval = request.POST.get('interval')
        
        print(f"Yangi qiymatlar: message={message}, interval={interval}")  # Debug
        
        try:
            # E'lonni to'xtatish
            was_active = announcement.is_active
            if was_active:
                announcement.is_active = False
                announcement.save()
                
            # Ma'lumotlarni yangilash    
            announcement.message = message
            announcement.interval = int(interval)
            announcement.save()
            
            messages.success(request, "E'lon muvaffaqiyatli yangilandi va to'xtatildi!")
            
        except Exception as e:
            print(f"Xato: {e}")  # Debug
            messages.error(request, f"Xatolik yuz berdi: {e}")
            
        return redirect('announcement:list')
        
    return render(request, 'announcement/edit.html', {
        'announcement': announcement
    })

@login_required
def start_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    if not announcement.is_active:
        announcement.is_active = True
        announcement.save()
        
        # Yangi thread boshlash
        start_announcement_thread(announcement)
        
        messages.success(request, "E'lon muvaffaqiyatli ishga tushirildi!")
    
    return redirect('announcement:list')

@login_required
def stop_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    announcement.is_active = False
    announcement.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('announcement:list')

@login_required
def delete_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    announcement.delete()
    return JsonResponse({'status': 'success'})

@login_required
def channel_list(request):
    channels = TelegramChannel.objects.all()
    return render(request, 'announcement/channel_list.html', {'channels': channels})

@login_required
def add_channel(request):
    if request.method == 'POST':
        channel_id = request.POST.get('channel_id', '').strip()
        name = request.POST.get('name', '').strip()
        
        if not channel_id or not name:
            messages.error(request, 'Kanal ID va nomi bo\'sh bo\'lishi mumkin emas!')
            return redirect('announcement:add_channel')
            
        # Chat ID ni tozalash va formatlash
        clean_id = channel_id.replace('@', '').strip()
        
        if clean_id.isdigit():
            # Raqamli ID
            raw_id = clean_id  # Asl ID ni saqlab qo'yamiz
            formatted_id = f"-100{clean_id}"  # Telegram formatidagi ID
        elif clean_id.startswith('-100'):
            raw_id = clean_id[4:]  # -100 ni olib tashlaymiz
            formatted_id = clean_id
        elif clean_id.startswith('-'):
            raw_id = clean_id[1:]  # - ni olib tashlaymiz
            formatted_id = f"-100{raw_id}"
        else:
            # Username
            raw_id = clean_id
            formatted_id = f"@{clean_id}"

        # Mavjud chat ID larni tekshirish
        existing = TelegramChannel.objects.filter(
            channel_id__in=[formatted_id, f"@{clean_id}", clean_id]
        ).first()
        
        if existing:
            messages.error(request, f'Bu kanal allaqachon mavjud! ({raw_id})')
            return redirect('announcement:channel_list')

        try:
            channel = TelegramChannel.objects.create(
                channel_id=formatted_id,
                channel_name=name if name != clean_id else raw_id,  # Agar nom ID bilan bir xil bo'lsa
                is_active=True
            )
            messages.success(request, f'Kanal muvaffaqiyatli qo\'shildi: {raw_id}')
        except Exception as e:
            messages.error(request, f'Xatolik yuz berdi: {str(e)}')
            
        return redirect('announcement:channel_list')
        
    return render(request, 'announcement/add_channel.html')

@login_required
def edit_channel(request, channel_id):
    channel = get_object_or_404(TelegramChannel, id=channel_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            channel.channel_name = name
            channel.save()
            messages.success(request, 'Kanal nomi muvaffaqiyatli o\'zgartirildi')
        return redirect('announcement:channel_list')
        
    return render(request, 'announcement/edit_channel.html', {'channel': channel})

@login_required
def toggle_channel(request, channel_id):
    channel = get_object_or_404(TelegramChannel, id=channel_id)
    channel.is_active = not channel.is_active
    channel.save()
    status = "yoqildi" if channel.is_active else "o'chirildi"
    messages.success(request, f'Kanal {status}')
    return redirect('announcement:channel_list')

@login_required
def delete_channel(request, channel_id):
    channel = get_object_or_404(TelegramChannel, id=channel_id)
    channel.delete()
    return redirect('announcement:channel_list')

@login_required
def profile_view(request):
    return render(request, 'announcement/profile.html')

@login_required
def settings_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        messages.success(request, 'Profil ma\'lumotlari yangilandi')
        return redirect('announcement:profile')
        
    return render(request, 'announcement/settings.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Joriy parol noto\'g\'ri')
            return redirect('announcement:change_password')
            
        if new_password1 != new_password2:
            messages.error(request, 'Yangi parollar mos kelmadi')
            return redirect('announcement:change_password')
            
        request.user.set_password(new_password1)
        request.user.save()
        messages.success(request, 'Parol muvaffaqiyatli o\'zgartirildi')
        return redirect('announcement:login')
        
    return render(request, 'announcement/change_password.html')

def some_view(request):
    try:
        # View logikasi
        with atomic():
            # Database operatsiyalari
            pass
            
    except OperationalError:
        # Database connection qayta tiklanadi
        connection.close()
        return redirect(request.path)
        
    except Exception as e:
        logger.error(f"Xato yuz berdi: {str(e)}")
        messages.error(request, "Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.")
        return redirect('announcement:list')
