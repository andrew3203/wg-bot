import os
from celery import Celery
from celery import shared_task
from celery.utils.log import get_task_logger


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wg_control.settings')

app = Celery('wg_control')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

logger = get_task_logger(__name__)


@shared_task
def send_notify(user_id, keyword, *args, **kwagrs):
    logger.info(
        f' - - - User: {user_id} notified! {keyword}, {args}, {kwagrs} - - -')
    return True
