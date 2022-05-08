from celery import shared_task
from wg_control.celery import app, send_notify
from celery import group
from celery.utils.log import get_task_logger
from django.core.management import call_command
from django.utils import timezone

from .models import User, VpnServer, Order, Peer
from .controllers import *
from .serializers import PeerSerializer, ServerTrafficSerializer
from email.mime.image import MIMEImage

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


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
    peers_list = conection.get_peers()

    recived_bytes = 0
    trancmitted_bytes = 0
    for peer in peers_list:
        public_key = peer['PublicKey']
        rel_peer = Peer.objects.filter(public_key=public_key).first()
        connected = True if peer['receive_bytes'] + peer['transmit_bytes'] > 0 else False
        
        peer_data = {
            'peer_id': peer['UID'],
            'public_key': public_key,
            'server': s.id,
            'last_handshake': peer['last_handshake'],
            'connected': connected,
            'recived_bytes': peer['receive_bytes'],
            'trancmitted_bytes': peer['transmit_bytes'],
        }

        serializer = PeerSerializer(data=peer_data, instance=rel_peer)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f'Peer {public_key[:10]} updated')

        recived_bytes += peer['receive_bytes']
        trancmitted_bytes += peer['transmit_bytes']

    traffic_server_data = {
        'recived_bytes': recived_bytes,
        'trancmitted_bytes': trancmitted_bytes,
        'server': s.id,
    }
    serializer = ServerTrafficSerializer(data=traffic_server_data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    logger.info(f'Servr {s.id} updated')


@shared_task(ignore_result=True)
def get_updates(vpn_server_ids=None):
    if vpn_server_ids is None:
        vpn_server_ids = VpnServer.objects.all().values_list('id', flat=True)
    tasks = [update_vpn_server.s(vpn_id) for vpn_id in vpn_server_ids]
    results = group(tasks)()
    logger.info('get_updates task!')

@shared_task(ignore_result=False)
def send_order_mail(user_id, order_id):
    logger.info(f' - - - - - - user {user_id}  order_id {order_id} - - - -  - - - - -')
    order = Order.objects.get(id=order_id)
    user = User.objects.get(id=user_id)
    context = order.get_peers_context()

    html_content = render_to_string('api/order.html', context=context)#.strip()
    msg = EmailMultiAlternatives(
       subject='Спасибо, что воспользовались нашим сервисом!',
       body=html_content,
       from_email='',
       to=[user.email],
    )
    msg.content_subtype = 'html'
    
    try:
        r = msg.send()
        logger.info('Mail sent!')
        if r:
            return {'results': 'done'}
        
        return {'results': 'done?'}
    except Exception as e:
        return {'results': 'error', 'ditails': f"{e}"}
    
    
