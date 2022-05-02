from http import client
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from wg_control.settings import DAYS_PIRIOD


from . import models


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Client
        fields = (
            'id',
            'clientname', 'password',
            'is_active', 'is_staff', 'created_at'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'is_active': {'read_only': True},
            'created_at': {'read_only': True},
            'is_staff': {'read_only': True},
        }

    def create(self, validated_data):
        client = models.Client.objects.create(
            clientname=validated_data.pop('clientname'),
            **validated_data
        )
        client.set_password(validated_data['password'])
        client.save()
        return client


class UserSerializer(serializers.ModelSerializer):

    client = ClientSerializer()

    class Meta:
        model = models.User
        fields = (
            'client', 'id',
            'tg_user_id', 'email',
            'first_name', 'last_name', 'language_code',
            'balance', 'created_at', 'updated_at'
        )
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'is_staff': {'read_only': True},
        }
        depth = 1

    def create(self, validated_data):
        client_data = validated_data.pop('client')

        client = models.Client(clientname=client_data['clientname'])
        client.set_password(client_data['password'])
        client.save()
        user = models.User(
            client=client,
            **validated_data
        )
        user.save()
        return user


class ReferralSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Referral
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'finish_at': {'read_only': True},
            # 'owner': {'read_only': True}
        }

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

    class Meta:
        model = models.Order
        fields = (
            'id', 'user',
            'tariff', 'is_paid',
            'paid_at', 'finish_at',
            'created_at'
        )
        extra_kwargs = {
            'paid_at': {'read_only': True},
            'finish_at': {'read_only': True},
            'created_at': {'read_only': True},
            'user': {'read_only': True},
        }
    """
    def create(self, validated_data):
        order = models.Order.objects.create(
            user=validated_data.pop('user'),
            tariff=validated_data['tariff']
        )
        order.save()
        return order

    def update(self, instance, validated_data):
        if validated_data['is_paid'] and not instance.is_paid:
            instance.paid_at = timezone.now()
            instance.finish_at = instance.paid_at + timedelta(days=DAYS_PIRIOD)
            instance.is_paid = True
            instance.save()

        return instance
    """


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
