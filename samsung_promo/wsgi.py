"""
WSGI config for samsung_promo project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Load .env file if it exists (for local/staging)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsung_promo.settings')

application = get_wsgi_application()
