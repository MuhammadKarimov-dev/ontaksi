from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Message

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=20)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'phone_number', 'telegram_id')

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Xabar matnini kiriting...',
                'rows': 4
            })
        } 