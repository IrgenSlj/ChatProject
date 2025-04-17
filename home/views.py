from django.shortcuts import render
import os

def home_view(request):
    manifesto_path = os.path.join('static', 'text', 'Manifesto.txt')
    manifesto_sections = []
    
    try:
        with open(manifesto_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Split the content into sections (split by lines starting with dot)
            sections = content.split('\n.')
            
            for section in sections:
                if section.strip():  # Skip empty sections
                    # Split each section into title and content
                    lines = section.strip().split('\n\n', 1)
                    if len(lines) == 2:
                        title = lines[0].strip('.')  # Remove any remaining dots
                        content = lines[1].strip()
                        manifesto_sections.append({
                            'title': title,
                            'content': content
                        })

    except FileNotFoundError:
        manifesto_sections = [{'title': 'Manifesto text not found', 'content': ''}]

    context = {
        'manifesto_sections': manifesto_sections
    }
    
    return render(request, 'home/home.html', context)