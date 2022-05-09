from celery import shared_task
from celery import group
from celery.utils.log import get_task_logger

from .models import User, VpnServer, Order, Peer
from .controllers import Conection
from .serializers import PeerSerializer, ServerTrafficSerializer

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from wg_control.settings import PEERS_AMOUNT_PER_SERVER

import requests



logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def hello():
    logger.info('Hello there!')


@shared_task(ignore_result=True)
def check_user(user_id):
    logger.info(f'User {user_id} updated')
    user = User.objects.get(id=user_id)
    for order in Order.objects.filter(user=user, is_closed=False, is_paid=True):
        is_vaild, data = order.order_is_valid()
        if not is_vaild:
            order.close()
            send_notify.delay(**data)

        else:
            data = order.check_notify()
            if data: send_notify.delay(**data)




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
    
    
@shared_task(ignore_result=True)
def send_notify(user_id, keyword, **kwagrs):
    logger.info(f'- - - - - - - User: {user_id} notified! {keyword}, {kwagrs} - - - - - - - ')
    _texts = {
        'has_no_avallible_traffic': 'К сожалению, Вы израсходовали весь доступный трафик ({0:.2f}ГБ) заказа № {1}.\n\nДоступ к системе приостановлен, но вы можете повторить заказ в разделе "Мои Заказы"',
        'has_no_avallible_time': 'Срок заказа № {0}\n истек. Вы израсходовали {1:.2f} из {2:.2f}ГБ.\nДоступ к системе приостановлен, но вы можете повторить заказ в разделе "Мои Заказы"',
        'order_auto_renewaled': 'Ваш заказ  № {0}\n истек, но мы автоматически продлили его!\n\nВы можете продолжать пользоваться услугами нашего сервиса!\n\nВыш текущий баланс: {1:.2f} ₽',
        'has_no_balance_to_auto_renewale': 'Ваш заказ  № {0}\n истек, к сожалению мы не смогли автоматически продлить его, из-за того, что на вашем счету недостадачто средств(\n\nВыш текущий баланс: {1:.2f} ₽',
        'order_closed': 'Срок заказа № {0}\n истек. Доступ к системе приостановлен, но вы можете повторить заказ в разделе "Мои Заказы"!',
        'user_get_from_referral': 'Ура!\nКто-то воспользовался Вашей реферальной ссылкой!\n\n Как только пользователь пополнит свой баланс на {0} ₽ в нашем сервисе, мы зачислем вам на баланс {1} ₽!',
        'time_is_running_out': 'Внимание!\n\nУважаемый {0}, срок вашего заказа № {1} подходит к концу. Заказ будет активен еще {2}, после этого доступ к системе будет приостановлен.\n\nПровертье, что на вашем балансе достаточно средств для автопродления заказа!\n\nЕсли вы не хотите, чтобы этот заказ обнавлялся автоматически, вы можете изменить это в настройках этого заказа, через меню "Мои Заказы"',
        'traffic_is_running_out': 'Внимание!\n\nУважаемый {0}, доступный траффик вашего заказа № {1} подходит к концу. У вас осталось еще {2} ГБ, после этого доступ к системе будет приостановлен.\n\nПровертье, что на вашем балансе достаточно средств для автопродления заказа!\n\nЕсли вы не хотите, чтобы этот заказ обнавлялся автоматически, вы можете изменить это в настройках этого заказа, через меню "Мои Заказы"',
        'user_from_referral_add_balance': 'Ура!\nПриглашенный вами пользователь пополнил свой баланс!\n\nКак и обещали, пополняем ваш баланс на {0}₽\n\nТеперь у Вас на счету {1} ₽!\n\nСпасибо, что используете наш сервис!',

    }
    user = User.objects.get(id=user_id)
    text = ''
    if keyword == 'has_no_avallible_traffic':
        # send_notify.delay(user.id, 'has_no_avallible_traffic', order_id=self.id)
        order = Order.objects.get(id=kwagrs['order_id'])
        text = _texts['has_no_avallible_traffic'].format(order.get_traffic_gb(), order.id)
    
    if keyword == 'has_no_avallible_time':
        # send_notify.delay(user.id, 'has_no_avallible_time', order_id=self.id)
        order = Order.objects.get(id=kwagrs['order_id'])
        text = _texts['has_no_avallible_time'].format(order.id, order.get_traffic_gb(), order.tariff.traffic_amount)
    
    if keyword == 'order_auto_renewaled':
        # send_notify.delay(user.id, 'order_auto_renewaled', order_id=self.id)
        text = _texts['order_auto_renewaled'].format(kwagrs['order_id'], user.balance)
    
    if keyword == 'has_no_balance_to_auto_renewale':
        # send_notify.delay(user.id, 'has_no_balance_to_auto_renewale', order_id=self.id)
        text = _texts['has_no_balance_to_auto_renewale'].format(kwagrs['order_id'], user.balance)
    
    if keyword == 'order_closed':
        # send_notify.delay(user.id, 'order_closed', order_id=self.id)
        text = _texts['order_closed'].format(kwagrs['order_id'])
    
    if keyword == 'user_get_from_referral':
        text = _texts['user_get_from_referral'].format(100, 50)  # на сколько пополнит, сколько вернеться
    
    if keyword == 'time_is_running_out':
        # send_notify.delay(self.user.id, 'time_is_running_out', order_id=self.id, delta_time=delta_time)
        delta_time = kwagrs['delta_time']
        text = _texts['time_is_running_out'].format(user.client.clientname, kwagrs['order_id'], delta_time)
    
    if keyword == 'traffic_is_running_out':
        # send_notify.delay(self.user.id, 'traffic_is_running_out', order_id=self.id, delta_traffic=delta_traffic)
        text = _texts['traffic_is_running_out'].format(user.client.clientname, kwagrs['order_id'], kwagrs['delta_traffic'])

    if keyword == 'user_from_referral_add_balance':
        text = _texts['user_from_referral_add_balance'].format(50, user.balance)

    data = {'text': text}
    print(text)
    try:
        res = requests.post(user.client.server, data=data)
    except Exception as e:
        print(e)