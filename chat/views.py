from django.shortcuts import render, redirect, get_object_or_404
from .models import ChatRoom, Message, AgentProfile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages
from django.utils import timezone  # Add this for timestamp handling
import json
import os
import logging
from django.utils.html import escape
from .ai_agents import get_agent_response, AGENT_CONFIGS

logger = logging.getLogger('chat')

# --- Utility for conversation context ---
def get_conversation_context(room, max_messages=5):
    try:
        messages = Message.objects.filter(room=room).order_by('-timestamp')[:max_messages]
        context = "\n".join(
            f"{msg.sender.username if msg.sender else 'AI'}: {msg.content}"
            for msg in reversed(messages)
        )
        return context
    except Exception as e:
        logger.error(f"Error getting conversation context: {e}")
        return ""

# --- Chat Room Views ---

@login_required
def chat_room_list(request):
    rooms = ChatRoom.objects.all()
    return render(request, 'chat/chat_room_list.html', {'rooms': rooms})

@login_required
def create_chat_room(request):
    if request.method == "POST":
        try:
            name = request.POST.get("name", "").strip()
            agent = request.POST.get("agent", "")

            if not name:
                messages.error(request, "Room name cannot be empty")
                return redirect('chat:create_chat_room')

            if agent not in AGENT_CONFIGS:
                messages.error(request, "Invalid agent selected")
                return redirect('chat:agents')

            room = ChatRoom.objects.create(
                name=name,
                agent=agent,
                created_by=request.user
            )
            logger.info(f"Chat room '{name}' created by {request.user.username}")
            return redirect('chat:chat_room', room_id=room.id)
        except Exception as e:
            logger.error(f"Error creating chat room: {e}")
            messages.error(request, "Failed to create chat room")
            return redirect('chat:create_chat_room')

    # Pre-fill agent from query parameter
    suggested_agent = request.GET.get('agent', 'june')
    if suggested_agent not in AGENT_CONFIGS:
        suggested_agent = 'june'
    
    return render(request, 'chat/create_chat_room.html', {
        'agents': AGENT_CONFIGS,
        'suggested_agent': suggested_agent
    })

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    messages = Message.objects.filter(room=room).order_by('timestamp')
    return render(request, 'chat/chat_room.html', {'room': room, 'messages': messages, 'rooms': ChatRoom.objects.all(), 'current_room': room})

# --- AJAX/JSON Endpoints ---

@csrf_exempt
@login_required
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            chat_room_id = data.get('chat_room_id')
            message_content = data.get('message')

            if not chat_room_id or not message_content:
                return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)

            room = ChatRoom.objects.get(id=chat_room_id)
            message = Message.objects.create(
                room=room,
                sender=request.user,
                content=message_content,
                is_ai=False
            )

            logger.info(f"Message sent in room {room.id} by {request.user.username}")
            return JsonResponse({'status': 'success', 'message': 'Message sent'})

        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except ChatRoom.DoesNotExist:
            logger.error(f"Chat room {chat_room_id} not found")
            return JsonResponse({'status': 'error', 'message': 'Chat room not found'}, status=404)
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def get_ai_response(request):
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    chat_room_id = request.GET.get('chat_room_id')
    message = request.GET.get('message')

    if not chat_room_id or not message:
        return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)

    try:
        room = ChatRoom.objects.get(id=chat_room_id)
        agent_name = room.agent

        if agent_name not in AGENT_CONFIGS:
            logger.warning(f"Invalid agent requested: {agent_name}")
            return JsonResponse({'status': 'error', 'message': 'Invalid agent'}, status=400)

        # Get conversation context with error handling
        context = get_conversation_context(room)
        if context is None:
            logger.error(f"Failed to get conversation context for room {room.id}")
            return JsonResponse({'status': 'error', 'message': 'Failed to get conversation context'}, status=500)
        
        # Get response from agent
        ai_response = get_agent_response(agent_name, message, context)
        if not ai_response:
            logger.error(f"Empty response from agent {agent_name}")
            return JsonResponse({'status': 'error', 'message': 'Agent failed to generate response'}, status=500)
        
        # Escape HTML content to prevent XSS
        ai_response = escape(ai_response)

        # Save the message to the database
        Message.objects.create(
            room=room,
            sender=None,
            content=ai_response,
            is_ai=True
        )

        logger.info(f"Successfully generated AI response for room {room.id}")
        return JsonResponse({
            'status': 'success',
            'response': ai_response,
            'agent_name': AGENT_CONFIGS[agent_name]['name']
        })

    except ChatRoom.DoesNotExist:
        logger.warning(f"Chat room not found: {chat_room_id}")
        return JsonResponse({'status': 'error', 'message': 'Chat room not found'}, status=404)
    except Exception as e:
        error_message = f"Error generating AI response: {e}"
        logger.error(error_message)
        return JsonResponse({'status': 'error', 'message': error_message}, status=500)

@login_required
def get_messages(request, room_id):
    try:
        room = get_object_or_404(ChatRoom, id=room_id)
        messages = Message.objects.filter(room=room).order_by('timestamp')
        agent_display_name = AGENT_CONFIGS[room.agent]['name']  # Use actual agent name

        message_list = [
            {
                'sender': msg.sender.username if msg.sender else agent_display_name,
                'content': msg.content,
                'is_ai': msg.is_ai,
                'timestamp': msg.timestamp.isoformat(),
                'can_delete': msg.sender == request.user or request.user.is_staff
            }
            for msg in messages
        ]
        return JsonResponse(message_list, safe=False)
    except Exception as e:
        logger.error(f"Error getting messages for room {room_id}: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def delete_chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    try:
        if request.method == 'POST':
            name = room.name  # Store name for logging
            room.delete()
            logger.info(f"Chat room deleted: {name}")
            return redirect('chat:chat_room_list')
        return render(request, 'chat/chat_room_list.html', {'room': room})
    except Exception as e:
        logger.error(f"Error deleting chat room {room_id}: {e}")
        return JsonResponse({'status': 'error', 'message': 'Failed to delete chat room'}, status=500)

# --- Info/Utility Views ---

def agents(request):
    return render(request, 'chat/agents.html', {
        'agents': AGENT_CONFIGS
    })

def manifesto(request):
    manifesto_path = os.path.join(settings.BASE_DIR, 'static', 'text', 'manifesto.txt')
    try:
        with open(manifesto_path, encoding='utf-8') as f:
            manifesto_text = f.read()
    except FileNotFoundError:
        manifesto_text = "Manifesto not available."
    return render(request, 'chat/manifesto.html', {'manifesto_text': manifesto_text})

def chat_view(request):
    return redirect('chat:chat_room_list')

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    room_id = message.room.id
    if request.method == 'POST':
        if request.user == message.sender or request.user.is_staff:
            message.delete()
            logger.info(f"Message {message_id} deleted by {request.user.username}")
            return redirect('chat:chat_room', room_id=room_id)
        else:
            logger.warning(f"Unauthorized deletion attempt of message {message_id} by {request.user.username}")
            return JsonResponse({'status': 'error', 'message': 'Not allowed'}, status=403)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def clear_conversation(request, room_id):
    if request.method == 'POST':
        try:
            room = get_object_or_404(ChatRoom, id=room_id)
            deleted_count, _ = Message.objects.filter(room=room).delete()
            logger.info(f"Conversation cleared in room {room_id} by {request.user.username}. {deleted_count} messages deleted.")
            return JsonResponse({'status': 'success', 'message': f'{deleted_count} messages deleted'})
        except Exception as e:
            logger.error(f"Error clearing conversation in room {room_id}: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)