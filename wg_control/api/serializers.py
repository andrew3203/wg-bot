from asyncore import read
from http import client
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from wg_control.settings import DAYS_PIRIOD, REWARD
from wg_control.celery import send_notify



from . import models


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Client
        fields = '__all__'
        read_only_fields = (
            'id',
            'groups', 'user_permissions',
            'is_active', 'is_staff', 'is_superuser',
            'created_at', 'last_login',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        client = models.Client.objects.create_user(
            clientname=validated_data.pop('clientname'),
            password=validated_data.pop('password', None),
            **validated_data
        )
        return client


class UserSerializer(serializers.ModelSerializer):

    invited_through_referral = serializers.SlugRelatedField(
        slug_field='code', 
        required=False, default=None, allow_null=True,
        queryset=models.Referral.objects.all(),
        read_only=False
    )

    client = ClientSerializer()

    class Meta:
        model = models.User
        fields = '__all__'
        read_only_fields = (
            'updated_at',
            'created_at',
            'balance'
        )
        depth = 1

    def create(self, validated_data):
        client_data = validated_data.pop('client')
        client = models.Client.objects.create_user(
            clientname=client_data.pop('clientname'),
            password=client_data.pop('password', None),
            **client_data
        )
        user = models.User.objects.create(
            client=client,
            **validated_data
        )
        user.save()
        referral = user.invited_through_referral
        if referral:
            send_notify.delay(referral.owner.id, 'user_get_from_referral', user=user.id)
            models.set_payment_listener(referral, user)
        return user
    
    def update(self, instance, validated_data):
        client_data = validated_data.pop('client')
        models.Client.objects.get(id=client_data['id']).update(**client_data)
        return super(self, UserSerializer).update(instance, validated_data)


class ReferralSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Referral
        fields = '__all__'
        read_only_fields = ('created_at', 'code', 'reward')

    """    
    def create(self, validated_data):
        referral = models.Referral.objects.create(
            owner=validated_data.pop('user'),
            code=validated_data.pop('code')
        )
        referral.save()
        return referral
    """


class OrderSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(
        queryset=models.User.objects.all(),
        many=False, 
        required=True
    )
    server = serializers.PrimaryKeyRelatedField(
        queryset=models.VpnServer.objects.all(),
        many=False, 
        required=True
    )
    peers = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )
    tariff = serializers.PrimaryKeyRelatedField(
        queryset=models.Tariff.objects.all(),
        many=False, 
        required=True
    )

    class Meta:
        model = models.Order
        fields = '__all__'
        read_only_fields = (
            'paid_at', 'finish_at',
            'created_at', 'is_closed', 'is_paid'
        )

    
    def create(self, validated_data):
        validated_data.pop('user')
        server = validated_data['server']
        tariff = validated_data['tariff']
        peers = models.VpnServer.get_peer_ids(server, tariff)
        order = models.Order.objects.create(
            user=validated_data.pop('real_user'),
            **validated_data
        )
        order.peers.set(peers)
        order.save()
        models.Peer.objects.filter(id__in=peers).update(is_booked=True)
        return order

    def update(self, instance, validated_data):
        if validated_data['is_paid'] and not instance.is_paid:
            instance.paid_at = timezone.now()
            instance.finish_at = instance.paid_at + timedelta(days=DAYS_PIRIOD)
            instance.is_paid = True
            instance.save()
        
        if validated_data['is_closed'] and not instance.is_closed:
            instance.is_closed = True
            instance.save()

        return instance
    


class TariffSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tariff
        fields = '__all__'


class VpnServerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.VpnServer
        fields = '__all__'


class PeerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Peer
        fields = '__all__'


class ServerTrafficSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ServerTraffic
        fields = '__all__'
