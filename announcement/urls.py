from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='announcement/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('send-message/', views.send_message, name='send_message'),
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/create/', views.create_announcement, name='create_announcement'),
    path('announcements/<int:announcement_id>/start/', views.start_announcement, name='start_announcement'),
    path('announcements/<int:announcement_id>/stop/', views.stop_announcement, name='stop_announcement'),
    path('announcements/<int:announcement_id>/delete/', views.delete_announcement, name='delete_announcement'),
    path('announcements/<int:announcement_id>/edit/', views.edit_announcement, name='edit_announcement'),
    path('channels/', views.channel_list, name='channel_list'),
    path('channels/add/', views.add_channel, name='add_channel'),
    path('channels/<int:channel_id>/toggle/', views.toggle_channel, name='toggle_channel'),
    path('channels/<int:channel_id>/delete/', views.delete_channel, name='delete_channel'),
    path('verify-user/<int:user_id>/', views.verify_user, name='verify_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('add-user/', views.add_user, name='add_user'),
    path('send-verification-sms/', views.send_verification_sms, name='send_verification_sms'),
]