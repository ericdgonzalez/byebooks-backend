"""
WSGI config for byebooks project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.append('/var/www/html/byebooks/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "byebooks.settings")

application = get_wsgi_application()
