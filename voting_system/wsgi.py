"""
Django's WSGI entry point. This file contains the WSGI configuration.
It tells the server HOW to serve the application.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voting_system.settings')

application = get_wsgi_application()

