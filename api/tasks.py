from celery import shared_task
from celery.utils.log import get_task_logger

from .models import *
logger = get_task_logger(__name__)

@shared_task
def hello():
    logger.info('Hello there!')