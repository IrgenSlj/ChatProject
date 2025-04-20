import os
from django.conf import settings
from django.shortcuts import render

def home(request):
    summary_path = os.path.join(settings.BASE_DIR, 'static', 'text', 'summary.txt')
    summary_text = ""
    try:
        with open(summary_path, encoding='utf-8') as f:
            summary_text = f.read()
    except FileNotFoundError:
        summary_text = "Summary not available."
    return render(request, 'home/home.html', {'summary_text': summary_text})