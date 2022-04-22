from codecs import ignore_errors
from celery import shared_task
from wg_control.celery import app
from celery import group
from celery.utils.log import get_task_logger
from django.core.management import call_command

from .models import *

logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def hello():
    logger.info('Hello there!')


@shared_task(ignore_result=True)
def check_user(user_id):
    logger.info(f'User {user_id} updated')
    return 1


@shared_task(ignore_result=True)
def check_users(user_ids):
    tasks = [check_user.s(user_id) for user_id in user_ids]
    results = group(tasks)()
    logger.info(f'{results}')
    logger.info('check_users task!')


@shared_task(ignore_result=True)
def update_vpn_server(vpn_server_id):
    logger.info(f'Servr {vpn_server_id} updated')
    return 1


@shared_task(ignore_result=True)
def get_updates(vpn_server_ids):
    tasks = [update_vpn_server.s(vpn_id) for vpn_id in vpn_server_ids]
    results = group(tasks)()
    logger.info(f'{results}')
    logger.info('get_updates task!')


@shared_task(ignore_result=True)
def send_mail():
    logger.info('Mail sent!')


@shared_task
def send_notify(user_id):
    logger.info('Done!')
    return True