from rest_framework import serializers
from . import models
from api.models import Client, User, Order


class OrderRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.OrderRequest
        fields = '__all__'
        depth = 2

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        client_data = user_data.pop('client')
        client, is_created_1 = Client.objects.get_or_create(
            clientname=client_data.pop('clientname'),
            password=client_data.pop('password', None),
            **client_data
        )
        user, is_created_2 = User.objects.get_or_create(
            client=client,
            **user_data
        )
        order, is_created_3 =  Order.objects.get_or_create(
            **validated_data
        )   
        if is_created_3:
            order_request = models.OrderRequest.objects.create(
                user=user,
                order=order
            )   
            return order_request
        else:
            return order



class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Refiew
        fields = '__all__'
