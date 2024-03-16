"""
ASGI config for GameGeek project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import uvicorn
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GameGeek.settings')

application = get_asgi_application()

# Optional: Set custom host and port
if __name__ == "__main__":
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 10000))
    uvicorn.run(application, host=host, port=port)

