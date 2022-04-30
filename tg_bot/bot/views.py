import requests
from celery_settings import app
from celery.utils.log import get_task_logger

from conf import TG_CLIENT_PASSWORD, TG_CLIENT_TOKEN, TG_CLIENT_NAME


logger = get_task_logger(__name__)


class Client(object):

    def __init__(self) -> None:
        self.clientname = TG_CLIENT_NAME
        self.password = TG_CLIENT_PASSWORD
        self.token = TG_CLIENT_TOKEN

    def login():
        pass

    def get_headers():
        pass

class User(object):

    def __init__(self) -> None:
        pass

    def create():
        pass

    def get():
        pass

    
    @staticmethod
    @app.task()
    def get_user(user_id):
        logger.info(f'User {user_id} data resivied')

    def update(*args, **kwargs):
        pass

    @staticmethod
    @app.task()
    def update_user(user_id, *args, **kwargs):
        logger.info(f'User {user_id} data updated')


    def update():
        pass

    def get_orders_list() -> list:
        pass


class Order(object):

    def __init__(self) -> None:
        pass

    def create(*args, **kwargs):
        pass

    def get(tg_id):
        pass
    
    #@celery_app.task(name='get_order')
    @staticmethod
    def get_order(order_id):
        pass

    def update(*args, **kwargs):
        pass
    
    #@celery_app.task(name='order_update')
    @staticmethod
    def order_update(order_id, *args, **kwargs):
        pass

    def delete():
        pass


class VpnServer(object):

    def __init__(self) -> None:
        pass
    
    #@celery_app.task(name='get_vpns_list')
    @staticmethod
    def get_vpns_list():
        pass
    
    def get():
        pass
    
    #@celery_app.task(name='get_vpn')
    @staticmethod
    def get_vpn(vpn_id):
        pass


