from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify/<int:user_id>/', views.verify_sms, name='verify_sms'),
] 