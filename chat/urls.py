from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_room_list, name='chat_room_list'),
    path('rooms/', views.chat_room_list, name='chat_room_list'),
    path('create/', views.create_chat_room, name='create_chat_room'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('message/delete/<int:message_id>/', views.delete_message, name='delete_message'),
    path('room/delete/<int:room_id>/', views.delete_chat_room, name='delete_chat_room'),
    path('message/send/', views.send_message, name='send_message'),
    path('get_ai_response/', views.get_ai_response, name='get_ai_response'),
    path('get_messages/<int:room_id>/', views.get_messages, name='get_messages'),
    path('agents/', views.agents, name='agents'),
    path('manifesto/', views.manifesto, name='manifesto'),
    path('room/<int:room_id>/clear/', views.clear_conversation, name='clear_conversation'),
]