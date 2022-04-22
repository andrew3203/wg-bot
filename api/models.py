from faulthandler import enable
from http import client
from re import T, U
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

from django.utils.translation import gettext_lazy as _


class UserProfileManager(BaseUserManager):
    def create_user(self, clientname, password, **extra_fields):
        email = extra_fields.get('email', None)
        if email:
            extra_fields['email'] =  self.normalize_email(email) 
        password = self.make_random_password() if not password else password

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
    code = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    finish_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self) -> str:
        return f'{self.code}'

    def get_link(self):
        pass

    def is_active(self):
        pass

    def get_uses_amount(self):
        return User.objects.filter(invited_through_referral=self).count()
    
    get_uses_amount.allow_tags = True


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
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)
    finish_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f'Order {self.id}: {self.tariff}'



class Tariff(models.Model):
    price = models.IntegerField()
    traffic_amount = models.IntegerField()
    connections_amount = models.IntegerField(default=0)

    def __str__(self):
        return f'Tariff: t{self.traffic_amount}GB, p{self.price}, c{self.connections_amount}'


class VpnServer(models.Model):
    ip = models.CharField(max_length=70)
    location = models.CharField(max_length=70)
    peers_amount = models.IntegerField(default=0)

    def __str__(self):
        return f'Server: {self.location}'

    def get_available_peers_list(self):
        return Peer.objects.filter(server=self)

    def get_available_peers_amount(self):
        return self.get_available_peers_list().count()

    def get_peers_amount(self):
        return Peer.objects.filter(server=self).count()

    def get_traffic_list(self):
        return ServerTraffic.objects.filter(server=self)

    def get_traffic(self):
        amount = 0
        for obj in self.get_traffic_list():
            amount += obj.get_traffic()
        return amount

    def update_traffic(self):
        new_traffic = ServerTraffic()
        for peer in self.get_available_peers_list():
            recived_gb, trancmitted_gb = peer.get_traffic()
            new_traffic.recived_gb += recived_gb
            new_traffic.trancmitted_gb += trancmitted_gb
        new_traffic.save()


class Peer(models.Model):
    peer_id = models.CharField(unique=True, max_length=150)
    public_key = models.CharField(unique=True, max_length=150)
    server = models.ForeignKey(  # many-to-one
        'VpnServer',
        on_delete=models.CASCADE,
    )
    last_handshake = models.DateTimeField(blank=True, null=True)

    is_booked = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)
    connected = models.BooleanField(default=False)

    def __str__(self):
        return f'Peer: {self.id}'

    def unbooke(self):
        self.server.update_traffic()
        self.is_busy = False
        self.save()

    def get_qrcode(self):
        # TODO
        pass

    def get_config_file(self):
        # TODO
        pass

    def get_traffic_list(self):
        return PeerTraffic.objects.filter(peer=self)

    def get_traffic(self):
        recived_gb = 0
        trancmitted_gb = 0
        for obj in self.get_traffic_list():
            recived_gb += obj.recived_gb
            trancmitted_gb += obj.trancmitted_gb
        return recived_gb, trancmitted_gb

    def get_all_traffic(self):
        recived_gb, trancmitted_gb = self.get_traffic()
        return recived_gb + trancmitted_gb

    def update_traffic(self):
        # TODO: conect to api
        pass


class BaseTraffic(models.Model):
    time = models.DateTimeField(auto_now_add=True, db_index=True)
    recived_gb = models.IntegerField(default=0)
    trancmitted_gb = models.IntegerField(default=0)

    def __str__(self):
        return f'Traffic: {self.id}'

    def _convert_to_gb(self):
        # TODO
        pass

    def get_traffic(self):
        return self.recived_gb + self.trancmitted_gb

    def set_traffic(self, recived, trancmitted):
        self.recived_gb = self._convert_to_gb(recived)
        self.trancmitted_gb = self._convert_to_gb(trancmitted)


class PeerTraffic(BaseTraffic):
    peer = models.ForeignKey(  # many-to-one
        'Peer',
        on_delete=models.CASCADE,
    )


class ServerTraffic(BaseTraffic):
    server = models.ForeignKey(  # many-to-one
        'VpnServer',
        on_delete=models.CASCADE,
    )

    def update_traffic(self, recived_gb, trancmitted_gb):
        self.recived_gb += recived_gb
        self.trancmitted_gb += trancmitted_gb
