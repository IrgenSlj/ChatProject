from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Message, ChatRoom
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .ai_agents import get_agent_response, AGENT_PROFILES
import os
import json

# --- Utility for conversation context ---
def get_conversation_context(room):
    messages = Message.objects.filter(room=room).order_by('-timestamp')
    context = "\n".join(
        f"{msg.sender.username if msg.sender else AGENT_PROFILES.get(room.agent, {}).get('display_name', 'Agent')}: {msg.content}"
        for msg in messages
    )
    return context

# --- Chat Room Views ---

@login_required
def chat_room_list(request):
    rooms = ChatRoom.objects.all()
    return render(request, 'chat/chat_room_list.html', {'rooms': rooms})

@login_required
def create_chat_room(request):
    if request.method == "POST":
        name = request.POST["name"]
        agent = request.POST["agent"]
        ChatRoom.objects.create(name=name, agent=agent)
        return redirect('chat_room_list')
    return render(request, 'chat/create_chat_room.html')

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    if request.method == "POST":
        user_msg = request.POST["message"]
        Message.objects.create(room=room, sender=request.user, content=user_msg, is_ai=False)
        context = get_conversation_context(room)
        ai_response = get_agent_response(room.agent, user_msg, context=context)
        Message.objects.create(room=room, sender=None, content=ai_response, is_ai=True)
        return redirect('chat_room', room_id=room.id)
    messages = Message.objects.filter(room=room).order_by('-timestamp')
    return render(request, 'chat/chat_room.html', {'room': room, 'messages': messages})

# --- AJAX/JSON Endpoints ---

@csrf_exempt
@login_required
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        chat_room_id = data.get('chat_room_id')
        if not chat_room_id:
            return JsonResponse({'status': 'error', 'message': 'No chat_room_id provided'}, status=400)
        try:
            room = ChatRoom.objects.get(id=chat_room_id)
        except ChatRoom.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Chat room not found'}, status=404)
        content = data.get('content', '')
        Message.objects.create(room=room, sender=request.user, content=content, is_ai=False)

        # Use the selected agent's LLM for the reply
        context = get_conversation_context(room)
        ai_response = get_agent_response(room.agent, content, context=context)
        Message.objects.create(room=room, sender=None, content=ai_response, is_ai=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def get_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    messages = Message.objects.filter(room=room).order_by('timestamp')
    agent_display_name = AGENT_PROFILES.get(room.agent, {}).get('display_name', 'Agent')
    message_list = [
        {
            'sender': msg.sender.username if msg.sender else agent_display_name,
            'content': msg.content,
            'is_ai': msg.is_ai
        }
        for msg in messages
    ]
    return JsonResponse(message_list, safe=False)

# --- Info/Utility Views ---

def agents(request):
    agent_profiles = [
        {"name": "June", "description": "The assistant and friendship model."},
        {"name": "Ludwig", "description": "The architect and designer."},
        {"name": "Gustav", "description": "The coder and engineer."},
        {"name": "Salvador", "description": "The artist and interactive content generator."},
    ]
    return render(request, 'chat/agents.html', {'agent_profiles': agent_profiles})

def manifesto(request):
    manifesto_path = os.path.join(settings.BASE_DIR, 'static', 'text', 'manifesto.txt')
    try:
        with open(manifesto_path, encoding='utf-8') as f:
            manifesto_text = f.read()
    except FileNotFoundError:
        manifesto_text = "Manifesto not available."
    return render(request, 'chat/manifesto.html', {'manifesto_text': manifesto_text})

def chat_view(request):
    return redirect('chat_room_list')

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    room_id = message.room.id
    # Optional: Only allow the sender or staff to delete
    if request.user == message.sender or request.user.is_staff:
        message.delete()
        return redirect('chat_room', room_id=room_id)
    return JsonResponse({'status': 'error', 'message': 'Not allowed'}, status=403)