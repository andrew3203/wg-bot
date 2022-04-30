import requests
from conf import TG_CLIENT_PASSWORD, TG_CLIENT_TOKEN, TG_CLIENT_NAME

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
    def get_user(user_id):
        pass

    def update(*args, **kwargs):
        pass

    @staticmethod
    def update_user(user_id, *args, **kwargs):
        pass

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

    @staticmethod
    def get(order_id):
        pass

    def update(*args, **kwargs):
        pass
    
    @staticmethod
    def order_update(order_id, *args, **kwargs):
        pass

    def delete():
        pass


class VpnServer(object):

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_vpns_list():
        pass
    
    def get():
        pass

    @staticmethod
    def get_vpn(vpn_id):
        pass


