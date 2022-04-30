import os
import logging
from datetime import timedelta


DEBUG = not not os.getenv("DJANGO_DEBUG", False)

# Telelgram bot token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Tg admin inf0
TG_CLIENT_NAME = os.getenv('TG_CLIENT_NAME')
TG_CLIENT_PASSWORD = os.getenv('TG_CLIENT_PASSWORD')
TG_CLIENT_TOKEN = os.getenv('TG_CLIENT_TOKEN')

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Redis
REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379')

# time when note in Redis  expires
DEFAULT_TIMEDELTA = timedelta(hours=1)

# Celery
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_ALWAYS_EAGER = DEBUG
