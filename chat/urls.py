from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('room/<int:chat_room_id>/', views.chat_room_view, name='chat_room'),
    path('send_message/', views.send_message, name='send_message'),
    path('get_messages/<int:chat_room_id>/', views.get_messages, name='get_messages'),
    path('manifesto/', views.manifesto, name='manifesto'),
]