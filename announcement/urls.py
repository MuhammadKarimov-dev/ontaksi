from django.urls import path
from . import views

app_name = 'announcement'  # URL namespace qo'shamiz

urlpatterns = [
    path('', views.announcement_list, name='list'),  # Asosiy sahifa
    path('edit/<int:announcement_id>/', views.edit_announcement, name='edit'),
    path('start/<int:announcement_id>/', views.start_announcement, name='start_announcement'),
    path('stop/<int:announcement_id>/', views.stop_announcement, name='stop_announcement'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('channels/', views.channel_list, name='channel_list'),  # Kanal ro'yxati
    path('channels/add/', views.add_channel, name='add_channel'),  # Kanal qo'shish
    path('channels/<int:channel_id>/toggle/', views.toggle_channel, name='toggle_channel'),
    path('channels/<int:channel_id>/delete/', views.delete_channel, name='delete_channel'),
    path('channels/<int:channel_id>/edit/', views.edit_channel, name='edit_channel'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('change-password/', views.change_password, name='change_password'),
]