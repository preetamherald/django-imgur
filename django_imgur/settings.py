from django.conf import settings

CONSUMER_ID = getattr(settings, 'IMGUR_CONSUMER_ID', None)
CONSUMER_SECRET = getattr(settings, 'IMGUR_CONSUMER_SECRET', None)
ACCESS_TOKEN = getattr(settings, 'IMGUR_ACCESS_TOKEN', None)
ACCESS_TOKEN_REFRESH = getattr(settings, 'IMGUR_ACCESS_TOKEN_REFRESH', None)
USERNAME = getattr(settings, 'IMGUR_USERNAME', None)
