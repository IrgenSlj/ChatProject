import os

# Default to development settings
settings_module = os.getenv('DJANGO_SETTINGS_MODULE', 'ChatProject.settings.development')

if settings_module == 'ChatProject.settings.development':
    from .development import *
else:
    from .production import *