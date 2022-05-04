from http import client
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from wg_control.settings import DAYS_PIRIOD


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
        return user
    
    def update(self, instance, validated_data):
        print(validated_data)
        client_data = validated_data.pop('client')
        models.Client.objects.get(id=client_data['id']).update(**client_data)
        return super(self, UserSerializer).update(instance, validated_data)


class ReferralSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Referral
        fields = '__all__'
        read_only_fields = ('created_at', 'code')

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

    peers = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = models.Order
        fields = '__all__'
        extra_kwargs = {
            'paid_at': {'read_only': True},
            'finish_at': {'read_only': True},
            'created_at': {'read_only': True},
            'is_closed': {'read_only': True},
            'is_paid': {'read_only': True},
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
