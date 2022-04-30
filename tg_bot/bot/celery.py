import os
from celery import Celery


os.environ.setdefault('TG_BOT_SETTINGS_MODULE', 'bot.conf')

app = Celery('bot')
app.config_from_object('bot.conf', namespace='CELERY')
app.autodiscover_tasks()
