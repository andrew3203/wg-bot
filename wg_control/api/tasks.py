from celery import shared_task
from wg_control.celery import app, send_notify
from celery import group
from celery.utils.log import get_task_logger
from django.core.management import call_command
from django.utils import timezone

from .models import User, VpnServer, Order, Peer
from .controllers import *
from .serializers import (
    VpnServerSerializer, PeerSerializer,
    ServerTrafficSerializer
)


logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def hello():
    logger.info('Hello there!')


@shared_task(ignore_result=True)
def check_user(user_id):
    logger.info(f'User {user_id} updated')
    user = User.objects.get(id=user_id)
    for order in Order.objects.filter(user=user):
        if not order.order_is_valid(user):
            order.close()



@shared_task(ignore_result=True)
def check_users(user_ids=None):
    if user_ids is None:
        user_ids = User.objects.all().values_list('id', flat=True)
    tasks = [check_user.s(user_id) for user_id in user_ids]
    results = group(tasks)()
    logger.info('check_users task!')


@shared_task(ignore_result=True)
def update_vpn_server(vpn_server_id):
    s = VpnServer.objects.get(id=vpn_server_id)
    logger.info(f' - - - - {s} {s.ip} - - - - -')
    conection = Conection(s.ip)
    peers_list = conection.get_peers_list()
    peers_list = sorted(peers_list, key=lambda el: el['name'])

    stats = conection.get_peer_stats_list()
    stats = sorted(stats, key=lambda el: el['name'])

    recived_bytes = 0
    trancmitted_bytes = 0
    for peer, stat in zip(peers_list, stats):
        public_key = peer['publicKey']
        rel_peer = Peer.objects.filter(public_key=public_key).first()
        if rel_peer is not None and rel_peer.trancmitted_bytes > stat['transmittedBytes']:
             stat['transmittedBytes'] += rel_peer.trancmitted_bytes
             stat['recived_bytes'] += rel_peer.recived_bytes
        
        peer_data = {
            'peer_id': peer['id'],
            'public_key': public_key,
            'server': vpn_server_id,
            'last_handshake': stat['lastHandshake'],
            'enabled': peer['enable'],
            'connected': stat['connected'],

            'recived_bytes': stat['receivedBytes'],
            'trancmitted_bytes': stat['transmittedBytes'],
        }

        serializer = PeerSerializer(data=peer_data, instance=rel_peer)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f'Peer {public_key[:10]} updated')

        recived_bytes += stat['receivedBytes']
        trancmitted_bytes += stat['transmittedBytes']

    traffic_server_data = {
        'recived_bytes': recived_bytes,
        'trancmitted_bytes': trancmitted_bytes,
        'server': vpn_server_id,
    }
    serializer = ServerTrafficSerializer(data=traffic_server_data)
    serializer.is_valid(raise_exception=True)
    server_traffic = serializer.save()
    
    if len(VpnServer.objects.all()) > 1:
        prev_traffic = VpnServer.objects.all()[1]
        if server_traffic.trancmitted_bytes < prev_traffic.trancmitted_bytes:
            server_traffic.recived_bytes += prev_traffic.recived_bytes
            server_traffic.trancmitted_bytes += prev_traffic.trancmitted_bytes
            server_traffic.save()

    logger.info(f'Servr {vpn_server_id} updated')


@shared_task(ignore_result=True)
def get_updates(vpn_server_ids=None):
    if vpn_server_ids is None:
        vpn_server_ids = VpnServer.objects.all().values_list('id', flat=True)
    tasks = [update_vpn_server.s(vpn_id) for vpn_id in vpn_server_ids]
    results = group(tasks)()
    logger.info('get_updates task!')


@shared_task(ignore_result=True)
def send_mail():
    logger.info('Mail sent!')
