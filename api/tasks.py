from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command #

from .models import *

logger = get_task_logger(__name__)

@shared_task
def hello():
    logger.info('Hello there!')


@shared_task
def update_traffic(user_ids):
    logger.info(user_ids)
    logger.info('update_traffic tsak!')
    #call_command("update_traffic", )

@shared_task
def check_users(user_ids):
    logger.info(user_ids)
    logger.info('check_users task!')
    #call_command("check_users", )


@shared_task
def update_peers(vpn_server_ids):
    logger.info(vpn_server_ids)
    logger.info('update_peers task!')
    # call_command("update_peers", )


