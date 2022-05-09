from http import server
from celery import shared_task
from celery import group
from celery.utils.log import get_task_logger

from .models import User, VpnServer, Order, Peer
from .controllers import Conection
from .serializers import PeerSerializer, ServerTrafficSerializer

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from wg_control.settings import PEERS_AMOUNT_PER_SERVER



logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def hello():
    logger.info('Hello there!')


@shared_task(ignore_result=True)
def check_user(user_id):
    logger.info(f'User {user_id} updated')
    user = User.objects.get(id=user_id)
    for order in Order.objects.filter(user=user, is_closed=False, is_paid=True):
        if not order.order_is_valid():
            order.close()
        else:
            order.check_notify()



@shared_task(ignore_result=True)
def check_users(user_ids=None):
    if user_ids is None:
        user_ids = User.objects.all().values_list('id', flat=True)
    tasks = [check_user.s(user_id) for user_id in user_ids]
    group(tasks)()
    logger.info('check_users task!')


@shared_task(ignore_result=True)
def update_vpn_server(vpn_server_id):
    s = VpnServer.objects.get(id=vpn_server_id)
    logger.info(f' - - - - {s} {s.ip} - - - - -')
    conection = Conection(s.ip)
    conection.set_api()
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
def send_order_mail(user_id, order_id, base_url):
    logger.info(f' - - - - - - user {user_id}  order_id {order_id} - - - -  - - - - -')
    order = Order.objects.get(id=order_id)
    user = User.objects.get(id=user_id)
    context = order.get_peers_context(base_url)

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


@shared_task(ignore_result=True)
def send_order_mails(orders_ids, base_url):
    base_url = base_url[:-16] + 'api/order/'
    data = []
    for order_id in orders_ids:
        o = Order.objects.get(id=order_id)
        data.append((o.user.id, o.id))
    tasks = [send_order_mail.s(d[0], d[1], f'{base_url}/{d[1]}/') for d in data]
    results = group(tasks)()
    logger.info('send_order_mails task!')


@shared_task(ignore_result=True)
def gen_peers(vpn_server_ids):
    if vpn_server_ids is None:
        vpn_server_ids = VpnServer.objects.all().values_list('id', flat=True)
    
    for server_id in vpn_server_ids:
        server = VpnServer.objects.get(id=server_id)
        to_do = PEERS_AMOUNT_PER_SERVER - len(Peer.objects.filter(server=server))
        if to_do > 0:
            con = Conection(server.ip)
            con.set_api()
            for i in range(to_do):
                con.add_peer()
        
    logger.info('gen_peers task!')
    
    
