import json
import requests
import time
import os

def make_request(f):

    def wrapper(self, num=0, *args, **kwargs):
        
        if num > 1:
            return None

        response, kw = f(self, *args, **kwargs)
        print(response.status_code)
        if response.status_code == 200:
            if kw:  
                return response.content
            else:
                return response.json()
        else:
            self.update_token()
            time.sleep(3)
            print(f'Token updated {num}')
            return wrapper(self, num=num+1, *args, **kwargs)

    return wrapper


class Conection(object):

    def __init__(self, base_ip, token=None) -> None:
        self.protocol = 'http://'
        self.base_ip = base_ip

        self.token = token if token else os.getenv('OAUTH_TOKEN')
        self.base_url = f'{self.protocol}{self.base_ip}'
        print(self.base_url)

    def update_token(self):
        pass

    def get_headers(self):
        return {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'x-wg-gen-web-auth': self.token
        }

    def update_base_url(self, protocol):
        self.protocol = protocol
        self.base_urlf = f'{self.protocol}{self.base_ip}'

    def _get_peers_url(self):
        return f'{self.base_url}/api/v1.0/client'

    def _get_peer_url(self, peer_id):
        return f'{self._get_peers_url()}/{peer_id}'

    def _get_peer_config_url(self, peer_id):
        return f'{self._get_peer_url(peer_id)}/config?qrcode=false'

    def _get_peer_qrcode_url(self, peer_id):
        return f'{self._get_peer_url(peer_id)}/config?qrcode=true'

    def _get_peers_stat_url(self):
        return f'{self.base_url}/api/v1.0/status/clients'

    @make_request
    def get_peers_list(self):
        url = self._get_peers_url()
        print(url)
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response, False

    @make_request
    def get_peer_stats_list(self):
        url = self._get_peers_stat_url()
        print(url)
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response, False

    @make_request
    def get_peer_config(self, peer_id):
        url = self._get_peer_config_url(peer_id)
        print(url)
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response, True

    @make_request
    def get_peer_qrcode(self, peer_id):
        url = self._get_peer_qrcode_url(peer_id)
        print(url)
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response, True

    @make_request
    def edit_peer(self, peer_id, data):
        url = self._get_peer_url(peer_id)
        print(url)
        headers = self.get_headers()
        data = json.dumps(data).encode('utf-8')
        response = requests.patch(url, headers=headers, data=data)
        return response, False

    @make_request
    def add_peer(self, name, email='', tags=[]):
        url = self._get_peers_url()
        data = {
            "name": name,
            "email": email,
            "enable": True,
            "allowedIPs":["0.0.0.0/0","::/0"],
            "address":["fd9f:6666::10:6:6:1/64","10.6.6.1/24"],
            "tags": tags
        }
        headers = self.get_headers()
        data = json.dumps(data).encode('utf-8')
        response = requests.post(url, headers=headers, data=data)
        return response, False

    @make_request
    def revoke_peer(self, peer_id):
        url = self._get_peer_url(peer_id)
        print(url)
        headers = self.get_headers()
        response = requests.delete(url, headers=headers)
        return response, False

    @make_request
    def get_peer(self, peer_id):
        url = self._get_peer_url(peer_id)
        print(url)
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response, False


