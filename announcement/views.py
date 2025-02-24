import asyncio
import threading
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from .models import Announcement, TelegramChannel
from bot_manager.telegram_bot import TelegramBot
import time
from django.contrib import messages 


announcement_tasks = {}
bot = TelegramBot()

# ✅ Asosiy asyncio event loop yaratamiz
main_loop = asyncio.new_event_loop()

# ✅ Event loopni fon thread'da ishga tushiramiz
def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    try:
        loop.run_forever()
    except RuntimeError:
        pass  # Agar loop yopilib qolsa, uni qayta ochishimiz kerak

event_thread = threading.Thread(target=start_event_loop, args=(main_loop,), daemon=True)
event_thread.start()

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
class AnnouncementTask:
    def __init__(self, announcement_id, announcement, active_channels):
        self.announcement_id = announcement_id
        self.announcement = announcement
        self.active_channels = active_channels
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    async def send_messages(self):
        bot = TelegramBot()
        for channel in self.active_channels:
            try:
                print(f"📤 {channel.channel_id} ga xabar yuborilmoqda...")
                await bot.send_message(channel.channel_id, self.announcement.message)
            except Exception as e:
                print(f"❌ Xato yuz berdi: {e}")

    def run(self):
        print(f"⏳ Xabar yuborish boshlandi: {self.announcement_id}")
        while self.running:
            asyncio.run(self.send_messages())  # ✅ To‘g‘ri ishlaydigan asinxron kod
            time.sleep(self.announcement.interval * 60)
            

@login_required
def start_announcement(request, announcement_id):
    global announcement_tasks

    if announcement_id in announcement_tasks:
        announcement_tasks[announcement_id].stop()
        del announcement_tasks[announcement_id]

    announcement = Announcement.objects.get(id=announcement_id)
    active_channels = TelegramChannel.objects.filter(is_active=True)
    if active_channels.count() == 0:
        messages.error(request, 'Фаол каналлар топилмади!')
        return redirect('channel_list')
        
    task = AnnouncementTask(announcement_id, announcement, active_channels)
    announcement_tasks[announcement_id] = task
    task.start()

    return redirect('announcement_list')

@login_required
def stop_announcement(request, announcement_id):
    global announcement_tasks
    if announcement_id in announcement_tasks:
        announcement_tasks[announcement_id].stop()
        del announcement_tasks[announcement_id]
    return redirect('announcement_list')

@login_required
def delete_announcement(request, announcement_id):
    global announcement_tasks
    announcement = Announcement.objects.get(id=announcement_id)
    if announcement.user == request.user:
        if announcement_id in announcement_tasks:
            announcement_tasks[announcement_id].stop()
            del announcement_tasks[announcement_id]
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
    global announcement_tasks
    announcement = Announcement.objects.get(id=announcement_id)
    
    if request.method == 'POST':
        if announcement.user == request.user:
            announcement.message = request.POST.get('message')
            announcement.interval = int(request.POST.get('interval', 5))
            announcement.save()

            if announcement_id in announcement_tasks:
                announcement_tasks[announcement_id].stop()
                del announcement_tasks[announcement_id]
                messages.info(request, 'Эълон таҳрирланди. Қайта ишга тушириш учун "Бошлаш" тугмасини босинг.')
            return redirect('announcement_list')
    context = {'announcement': announcement}
    return render(request, 'announcement/edit.html', context)

@login_required
def announcement_list(request):
    announcements = Announcement.objects.filter(user=request.user).order_by('id')
    context = {
        'announcements': announcements,
        'active_announcements': list(announcement_tasks.keys())
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
