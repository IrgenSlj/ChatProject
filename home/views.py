import os
from django.conf import settings
from django.shortcuts import render, redirect

def home_view(request):
    if request.user.is_authenticated:
        # Redirect to the user's main chatroom or chatroom list
        return redirect('chat:chat_room_list')  # or 'chat_room', with appropriate args

    summary_path = os.path.join(settings.BASE_DIR, 'static', 'text', 'summary.txt')
    summary_text = ""
    try:
        with open(summary_path, encoding='utf-8') as f:
            summary_text = f.read()
    except FileNotFoundError:
        summary_text = "Summary not available."
    return render(request, 'home/home.html', {'summary_text': summary_text})