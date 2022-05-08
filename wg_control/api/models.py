from turtle import back
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .controllers import Conection
from wg_control.celery import send_notify
from random import randint


def gen_code():
    min_lenght, max_lenght = 10, 15
    lenght = randint(min_lenght, max_lenght)
    base = 'abcdefghijklomopqrstuvwsynzABCDEFGHIJKLOMOPQRSTUVWSYNZ'
    N = len(base)
    return 'pro_'+''.join([base[randint(0, N-1)] for i in range(lenght)])


class UserProfileManager(BaseUserManager):

    def get_or_create(self, clientname, password=None, **extra_fields):
        inst = self.filter(clientname=clientname).first()

        if inst is None:
            inst = self.create_user(self, clientname, password, **extra_fields)
            return inst, True
        else:
            return inst, False

    def create_user(self, clientname, password=None, **extra_fields):
        email = extra_fields.get('email', None)
        if email:
            extra_fields['email'] = self.normalize_email(email)
        password = self.make_random_password() if password is None else password

        if not clientname:
            raise ValueError(_('The clientname must be set'))

        user = self.model(clientname=clientname, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, clientname, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(clientname, password, **extra_fields)


class Client(AbstractBaseUser, PermissionsMixin):
    clientname = models.CharField(
        _('Nicname'),
        max_length=32,
        unique=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    server_addres = models.CharField(max_length=70, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = UserProfileManager()

    USERNAME_FIELD = 'clientname'

    def get_full_name(self):
        return f'{self.clientname}'

    def get_short_name(self):
        return f'{self.clientname}'

    def __str__(self):
        return f'{self.clientname}'


class User(models.Model):
    client = models.OneToOneField(
        'Client',
        related_name='user',
        on_delete=models.CASCADE
    )
    tg_user_id = models.PositiveBigIntegerField(blank=True, default=0)

    email = models.EmailField(max_length=255, blank=True)

    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)

    language_code = models.CharField(max_length=8, blank=True)
    balance = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    invited_through_referral = models.OneToOneField(
        'Referral',
        related_name='invited_through_referral',
        related_query_name='invited_through_referrals',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.client.clientname}'

    def get_invited_users_list(self):
        if self.invited_through_referral:
            return []
        else:
            return User.objects.filter(personal_referral=self.invited_through_referral)

    def get_invited_users_amount(self):
        return len(self.get_invited_users_list())


class Referral(models.Model):
    owner = models.OneToOneField(
        'User',
        on_delete=models.SET_NULL,
        null=True,
    )
    code = models.CharField(max_length=30, default=gen_code, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    finish_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.code}'

    def get_link(self):
        pass

    def is_active(self):
        return self.finish_at > timezone.now()

    def get_uses_amount(self):
        return User.objects.filter(invited_through_referral=self).count()

    get_uses_amount.allow_tags = True


class Tariff(models.Model):
    price = models.IntegerField()
    traffic_amount = models.IntegerField()
    connections_amount = models.IntegerField(default=0)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f'Tariff: t{self.traffic_amount}GB, p{self.price}, c{self.connections_amount}'


class VpnServer(models.Model):
    ip = models.CharField(max_length=70)
    location = models.CharField(max_length=70)

    def __str__(self):
        return f'Server: {self.location}'

    def get_available_peers_list(self):
        return Peer.objects.filter(server=self, is_booked=False)

    def get_available_peers_amount(self):
        return self.get_available_peers_list().count()

    def get_peers_amount(self):
        return Peer.objects.filter(server=self).count()

    def get_traffic_list(self):
        return ServerTraffic.objects.filter(server=self)

    def get_traffic(self):
        traffic = self.get_traffic_list().first()
        return traffic.get_traffic()

    def get_traffic_label(self):
        traffic = self.get_traffic_list().first()
        return f'{traffic.get_traffic_gb():.3f} GiB'
    
    def get_available_tariffs(self, amout=None):
        amount = self.get_available_peers_amount()
        tariffs = Tariff.objects.filter(connections_amount__lte=amount)
        return tariffs[:amout] if tariffs else tariffs

    @staticmethod
    def get_peer_ids(server, tariff):
        peers = Peer.objects.filter(server=server, is_booked=False).values_list('id', flat=True)
        return peers[:tariff.connections_amount]



class Peer(models.Model):
    peer_id = models.CharField(unique=True, max_length=150)
    public_key = models.CharField(unique=True, max_length=150)
    server = models.ForeignKey(  # many-to-one
        'VpnServer',
        on_delete=models.CASCADE,
    )
    last_handshake = models.DateTimeField(blank=True, null=True)

    is_booked = models.BooleanField(default=False)
    connected = models.BooleanField(default=False)

    data_time_update = models.DateTimeField(auto_now_add=True)
    recived_bytes = models.BigIntegerField(default=0)
    trancmitted_bytes = models.BigIntegerField(default=0)

    def __str__(self):
        return f'Peer: {self.id}'
    
    def get_file_url(self):
        return ''

    def unbooke(self):
        self.last_handshake = None

        self.is_booked = False
        self.connected = False

        self.recived_bytes = 0
        self.trancmitted_bytes = 0
        self.save()

    def get_qrcode(self):
        # TODO
        pass

    def get_config_file(self):
        # TODO
        pass

    def get_traffic(self):
        return self.recived_bytes + self.trancmitted_bytes

    def get_traffic_label(self):
        traffic = self.get_traffic() / 1024 ** 3
        return f'{traffic:.3f} GiB'


class Order(models.Model):
    user = models.ForeignKey(  # many-to-one
        'User',
        on_delete=models.CASCADE,
    )
    tariff = models.ForeignKey(  # one-to-one
        'Tariff',
        on_delete=models.SET_NULL,
        null=True
    )
    server = models.ForeignKey(  # one-to-one
        'VpnServer', 
        on_delete=models.SET_NULL,
        null=True
    )

    peers = models.ManyToManyField(
        Peer,
        related_name='order',
        null=True
    )

    auto_renewal = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)

    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)
    finish_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.id}: {self.tariff}'

    def order_is_valid(self, user):
        if self.is_paid and not self.is_closed:

            if self.finish_at > timezone.now():
                return True

            elif self.auto_renewal:

                if user.balance > self.tariff.price:
                    user.balance -= self.tariff.price
                    user.save()
                    send_notify.delay(
                        user, 'order_auto_renewaled', order_id=self.id)
                    return True

                else:
                    send_notify.delay(
                        user, 'have_no_balance_to_auto_renewale', order_id=self.id)
                    return False

            else:
                send_notify.delay(user, 'order_closed', order_id=self.id)
                return False

        else:
            return True

    def close(self):
        self.is_closed = True
        self.save()
        for peer in Peer.objects.filter(order=self):
            ip = peer.server.ip
            conect = Conection(ip)
            conect.revoke_peer(PublicKey=peer.public_key)
            peer.unbooke()
    
    def get_peers_context(self):
        con = Conection(self.server.ip)
        context = {
            'peer2': 'display: None;',
            'peer3': 'display: None;',
            'peer4': 'display: None;',
            'peer5': 'display: None;',
            'peer6': 'display: None;',
            'peer7': 'display: None;',
        }
        for i, peer in enumerate(self.peers.all()):
            i +=1
            qrcode = con.get_peer_qrcode(PublicKey=peer.public_key)
            qrcode_src = f"data:image/png;base64,{qrcode}"
            conf_url = peer.get_file_url()
            context[f'peer{i}'] = ''
            context[f'peer{i}_conf_url'] = conf_url
            context[f'peer{i}_qrcode_src'] = qrcode_src
        return context


class ServerTraffic(models.Model):
    server = models.ForeignKey(  # many-to-one
        'VpnServer',
        on_delete=models.CASCADE,
    )

    time = models.DateTimeField(auto_now_add=True, db_index=True)
    recived_bytes = models.BigIntegerField(default=0)
    trancmitted_bytes = models.BigIntegerField(default=0)

    class Meta:
        ordering = ['-time']

    def __str__(self):
        return f'Traffic: {self.id}'

    def get_traffic_gb(self):
        bs = self.get_traffic()
        return bs / 1024**3

    def get_traffic(self):
        return self.recived_bytes + self.trancmitted_bytes
