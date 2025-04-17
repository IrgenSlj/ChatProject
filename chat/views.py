from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Message, ChatRoom
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import models
import os

# LLM setup
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_NAME = r"deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16) # Set torch_dtype to use PyTorch
    print(f"Model dtype: {model.dtype}") # Check the model dtype
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device='cpu') # Specify device
    print("LLM loaded successfully.")
except Exception as e:
    print(f"Error loading LLM: {e}")
    generator = None

@login_required
def chat_view(request):
    chat_rooms = ChatRoom.objects.all()
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        if room_name:
            chat_room = ChatRoom.objects.create(name=room_name)
            chat_room.participants.add(request.user)
            return redirect('chat_room', chat_room_id=chat_room.id)
    return render(request, 'chat/chat.html', {'chat_rooms': chat_rooms})

@login_required
def chat_room_view(request, chat_room_id):
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    if request.user not in chat_room.participants.all():
        chat_room.participants.add(request.user)
    return render(request, 'chat/chat_room.html', {'chat_room': chat_room})

@csrf_exempt
@login_required
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        chat_room_id = data['chat_room_id']
        content = data['content']
        chat_room = ChatRoom.objects.get(id=chat_room_id)

        message = Message.objects.create(chat_room=chat_room, sender=request.user, content=content)

        # LLM response
        if generator:
            try:
                prompt = f"Chat history:\n"
                # Get last 5 messages
                recent_messages = Message.objects.filter(chat_room=chat_room).order_by('-timestamp')[:5]
                for msg in reversed(recent_messages):
                    prompt += f"{msg.sender.username}: {msg.content}\n"
                prompt += f"June: {content}\nVirtual Companion:"

                llm_response = generator(prompt, max_length=100, num_return_sequences=1)[0]['generated_text']
                llm_response = llm_response.replace(prompt, "").strip()
            except Exception as e:
                print(f"Error generating LLM response: {e}")
                llm_response = "I'm sorry, I couldn't generate a response."
        else:
            llm_response = "LLM is not available."

        Message.objects.create(chat_room=chat_room, sender=User.objects.first(), content=llm_response) # Assuming LLM is a user

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def get_messages(request, chat_room_id):
    chat_room = ChatRoom.objects.get(id=chat_room_id)
    messages = Message.objects.filter(chat_room=chat_room).order_by('timestamp')
    message_list = [{'sender': msg.sender.username, 'content': msg.content} for msg in messages]
    return JsonResponse(message_list, safe=False)

def my_view(request):
    # ... some code ...
    # Only use TensorFlow here
    import tensorflow as tf  # TensorFlow is loaded only when needed
    model = tf.keras.models.load_model('my_model.h5')
    # ... more code ...
    return render(request, 'my_template.html')