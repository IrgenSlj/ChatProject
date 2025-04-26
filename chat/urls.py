from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('<int:room_id>/', views.chat_room, name='chat_room'),
    path('send_message/', views.send_message, name='send_message'),
    path('get_messages/<int:room_id>/', views.get_messages, name='get_messages'),
    path('manifesto/', views.manifesto, name='manifesto'),
    path('rooms/', views.chat_room_list, name='chat_room_list'),
    path('rooms/create/', views.create_chat_room, name='create_chat_room'),
    path('agents/', views.agents, name='agents'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
]