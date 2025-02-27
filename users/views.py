from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import CustomUser, SMSCode
import random

def register(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        code = str(random.randint(100000, 999999))
        
        user = CustomUser.objects.create_user(
            phone=phone,
            password=password,
            is_active=False
        )
        SMSCode.objects.create(user=user, code=code)
        
        # Bu yerda SMS yuborish logikasi qo'shishingiz kerak
        print(f"SMS kod: {code}")  # Test uchun
        
        return redirect('verify_sms', user_id=user.id)
    return render(request, 'registration/register.html')

def verify_sms(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    if request.method == 'POST':
        code = request.POST.get('code')
        sms_code = SMSCode.objects.filter(user=user, code=code, is_used=False).first()
        
        if sms_code:
            user.is_active = True
            user.save()
            sms_code.is_used = True
            sms_code.save()
            login(request, user)
            return redirect('profile')
        else:
            return render(request, 'registration/verify.html', {'error': "Noto'g'ri kod"})
    return render(request, 'registration/verify.html') 