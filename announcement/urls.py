from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
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
]