import requests
import collections
import string
import uuid
import subprocess
import random
import qrcode
from wg_control.settings import API_AUTH_NAME, API_AUTH_PASSWORD, API_AUTH_TOKEN
from wg_control.settings import MEDIA_ROOT

from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client

import io


class ApiError(Exception):
    pass


def logHttp(response, *args, **kwargs):
    extra = {'req': response.request, 'res': response}


class WGPClient:
    def __init__(self, url, *auths):
        app = App._create_(url)
        auth = Security(app)
        for t, cred in auths:
            auth.update_with(t, cred)

        client = Client(auth)
        self.app, self.client = app, client

        self.client._Client__s.hooks['response'] = logHttp

    def call(self, name, **kwargs):
        op = self.app.op[name]
        req, resp = op(**kwargs)
        resp = self.client.request((req, resp))

        if 200 <= resp.status <= 299:
            pass
        elif 400 <= resp.status <= 499:
            raise ApiError(resp.data["Message"])
        elif 500 == resp.status:
            raise ValueError(resp.data["Message"])
        elif 501 == resp.status:
            raise NotImplementedError(name)
        elif 502 <= resp.status <= 599:
            raise ApiError(resp.data["Message"])
        return resp

    def GetDevice(self, **kwargs):
        return self.call("GetDevice", **kwargs).data

    def PatchDevice(self, **kwargs):
        return self.call("PatchDevice", **kwargs).data

    def PutDevice(self, **kwargs):
        return self.call("PutDevice", **kwargs).data

    def GetDevices(self, **kwargs):
        # FIXME - could return empty list?
        return self.call("GetDevices", **kwargs).data or []

    def DeletePeer(self, **kwargs):
        return self.call("DeletePeer", **kwargs).data

    def GetPeer(self, **kwargs):
        return self.call("GetPeer", **kwargs).data

    def PatchPeer(self, **kwargs):
        return self.call("PatchPeer", **kwargs).data

    def PostPeer(self, **kwargs):
        return self.call("PostPeer", **kwargs).data

    def PutPeer(self, **kwargs):
        return self.call("PutPeer", **kwargs).data

    def GetPeerDeploymentConfig(self, **kwargs):
        return self.call("GetPeerDeploymentConfig", **kwargs).data

    def PostPeerDeploymentConfig(self, **kwargs):
        return self.call("PostPeerDeploymentConfig", **kwargs).raw

    def GetPeerDeploymentInformation(self, **kwargs):
        return self.call("GetPeerDeploymentInformation", **kwargs).data

    def GetPeers(self, **kwargs):
        return self.call("GetPeers", **kwargs).data

    def DeleteUser(self, **kwargs):
        return self.call("DeleteUser", **kwargs).data

    def GetUser(self, **kwargs):
        return self.call("GetUser", **kwargs).data

    def PatchUser(self, **kwargs):
        return self.call("PatchUser", **kwargs).data

    def PostUser(self, **kwargs):
        return self.call("PostUser", **kwargs).data

    def PutUser(self, **kwargs):
        return self.call("PutUser", **kwargs).data

    def GetUsers(self, **kwargs):
        return self.call("GetUsers", **kwargs).data


def generate_wireguard_keys():
    """
    Generate a WireGuard private & public key
    Requires that the 'wg' command is available on PATH
    Returns (private_key, public_key), both strings
    """
    privkey = subprocess.check_output(
        "wg genkey", shell=True).decode("utf-8").strip()
    pubkey = subprocess.check_output(
        f"echo '{privkey}' | wg pubkey", shell=True).decode("utf-8").strip()
    return (privkey, pubkey)


KeyTuple = collections.namedtuple("Keys", "private public")


class Conection(object):

    def __init__(self, ip) -> None:
        self.stat_url = f'http://{ip}:8081'
        self.URL = f'http://{ip}:8080/swagger/doc.json'
        self.AUTH = {
            "api": ('ApiBasicAuth', (API_AUTH_NAME, API_AUTH_PASSWORD)),
            "general": ('GeneralBasicAuth', (API_AUTH_NAME, API_AUTH_PASSWORD))
        }
        self.DEVICE = "wg0"

       
    def set_general(self):
         self.c_general = WGPClient(self.URL, *[self.AUTH[i] for i in ["general"]])
    
    def set_api(self):
          self.c_api = WGPClient(self.URL, *[self.AUTH[i] for i in ["api"]])

    @property
    def andmail(self):
        return 'test+' + ''.join(
            [random.choice(string.ascii_lowercase + string.digits) for i in range(6)]) + '@example.org'

    def get_stats(self):
        headers = {
            'Authorization': f'Token {API_AUTH_TOKEN}',
            'Content-Type': 'application/json'
        }
        d = '{"jsonrpc": "2.0", "method": "ListPeers", "params": {}}'
        resp = requests.post(self.stat_url, headers=headers, data=d)
        peers = resp.json()['result']['peers']
        dat = {}
        for p in peers:
            dat[p['public_key']] = {
                'last_handshake': p['last_handshake'],
                'receive_bytes': p['receive_bytes'],
                'transmit_bytes': p['transmit_bytes'],
            }
        return dat

    def revoke_peer(self, PublicKey):
        return self.c_api.DeletePeer(PublicKey=PublicKey)

    def add_peer(self, IsDisabled=True):
        privkey, pubkey = generate_wireguard_keys()
        peer = {
            "UID": uuid.uuid4().hex,
            "Identifier": uuid.uuid4().hex,
            "DeviceName": self.DEVICE,
            "PublicKey": pubkey,
            "PrivateKey": privkey,
            "DeviceType": "client",
            "Email": self.andmail,
        }
        return self.c_api.PostPeer(DeviceName=self.DEVICE, Peer=peer)

    def edit_email_peer(self, PublicKey, Email):
        peer = self.c_api.GetPeer(PublicKey=PublicKey)
        peer['Email'] = Email
        return self.c_api.PutPeer(PublicKey=peer.PublicKey, Peer=peer)

    def get_peer_conf(self, PublicKey):
        res = self.c_general.GetPeerDeploymentConfig(PublicKey=PublicKey)
        return res[2:-2].replace('\\n', '\n')

    def get_peer_conf_file(self, PublicKey):
        conf = self.get_peer_conf(PublicKey)
        return bytes(conf,'utf-8')

    def get_peer_qrcode(self, PublicKey):
        conf = self.get_peer_conf(PublicKey)
        img = qrcode.make(conf)
 
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr

    def get_peers(self):
        stats = self.get_stats()
        res = []
        peers = self.c_api.GetPeers(DeviceName=self.DEVICE)
        for peer in peers:
            pk = peer['PublicKey']
            peer = {**peer, **stats[pk]}
            res.append(peer)
        return res
