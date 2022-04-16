from http import client
from rest_framework import serializers

from . import models


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Client
        fields = (
            'username', 'password',
            'is_active', 'is_staff', 'created_at'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'is_active': {'read_only': True},
            'created_at': {'read_only': True},
            'last_login':  {'read_only': True},

        }

    def create(self, validated_data):
        user = models.User.objects.create_user(
            username=validated_data.pop('username'),
            password=validated_data.pop('password'),
            **validated_data
        )
        return user


class UserSerializer(serializers.ModelSerializer):

    client = ClientSerializer()

    class Meta:
        model = models.User
        fields = (
            'client', 'username', 
            'user_id', 'email',
            'first_name', 'last_name', 'language_code',
            'balance', 'is_active', 'created_at', 'updated_at'

        )
        extra_kwargs = {
            'password': {'write_only': True},
            'is_active': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }
        depth = 1

    def create(self, validated_data):
        client = models.Client(
            username=validated_data.pop('username'),
            password=validated_data.pop('password'),
        )
        user = models.User.objects.create_user(
            username=validated_data.pop('username'),
            password=validated_data.pop('password'),
            **validated_data
        )
        return user


class ReferralSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Referral
        fields = '__all__'
        extra_kwargs = {'created_at': {'read_only': True}}


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Order
        fields = '__all__'


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


class PeerTrafficSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PeerTraffic
        fields = '__all__'
        depth = 0


class ServerTrafficSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ServerTraffic
        fields = '__all__'
        depth = 0
