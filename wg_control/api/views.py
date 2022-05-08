from multiprocessing import context
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken


from . import serializers
from . import models
from . import permissions as p
from . import tasks


class ClientViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.ClientSerializer
    queryset = models.Client.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAdminUser]


class UserViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.UserSerializer
    permission_classes = [p.IsOwnerOrAdminUser]
    queryset = models.User.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_superuser or self.request.user.is_staff:
            query_set = queryset
        else:
            query_set = queryset.filter(client__id=self.request.user.id)
        return query_set
    
    @action(methods=['GET'], detail=False, url_path='check_payment')
    def check_payment(self, request, *args, **kwargs):
        orders = models.Order.objects.filter(is_closed=True)
        res = serializers.OrderSerializer(orders, many=True)
        return Response(res.data)
    


class ReferralViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.ReferralSerializer
    permission_classes = [p.IsOwnerOrAdminUser]
    queryset = models.Referral.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_superuser or self.request.user.is_staff:
            query_set = queryset
        else:
            query_set = queryset.filter(owner__client=self.request.user)
        return query_set

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = models.User.objects.get(
    #         client=request.user,
    #     )
    #     serializer.save(user)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.OrderSerializer
    permission_classes = [p.IsOwnerOrAdminUser]
    queryset = models.Order.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_superuser or self.request.user.is_staff:
            query_set = queryset
        else:
            query_set = queryset.filter(user__client=self.request.user)

        return query_set

    @action(methods=['GET'], detail=False, url_path='closed_order')
    def closed_orders(self, request, *args, **kwargs):
        orders = models.Order.objects.filter(is_closed=True)
        res = serializers.OrderSerializer(orders, many=True)
        return Response(res.data)

    @action(methods=['GET'], detail=False, url_path='unpayid_orders')
    def unpayid_orders(self, request, *args, **kwargs):
        orders = models.Order.objects.filter(is_paid=False, is_closed=False)
        res = serializers.OrderSerializer(orders, many=True)
        return Response(res.data)

    @action(methods=['GET'], detail=False, url_path='current_orders')
    def current_orders(self, request, *args, **kwargs):
        orders = models.Order.objects.filter(is_paid=True, is_closed=False)
        res = serializers.OrderSerializer(orders, many=True)
        return Response(res.data)
    
    @action(methods=['POST'], detail=True)
    def send_order_mail(self, request, *args, **kwargs):
        res = tasks.send_order_mail.delay(user_id=request.user.user.id, order_id=self.get_object().id)
        return Response({'run': 'True'})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = request.user
        user = models.User.objects.get(
            id=request.data['user']) if client.is_staff or client.is_superuser else client.user
        serializer.save(real_user=user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TarifViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.TariffSerializer
    queryset = models.Tariff.objects.all()
    permission_classes = [p.ReadOnly | IsAdminUser]


class VpnServerViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.VpnServerSerializer
    queryset = models.VpnServer.objects.all()
    permission_classes = [p.ReadOnly | IsAdminUser]

    @action(methods=['GET'], detail=True)
    def available_tariffs(self, request, *args, **kwargs):
        server = self.get_object()
        tariffs = server.get_available_tariffs()
        res = serializers.OrderSerializer(tariffs, many=True)
        return Response(res.data)


class PeerViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.PeerSerializer
    queryset = models.Peer.objects.all()
    permission_classes = [p.ReadOnly | IsAdminUser]


class ServerTrafficViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.ServerTrafficSerializer
    queryset = models.ServerTraffic.objects.all()
    permission_classes = [IsAuthenticated | IsAdminUser]


class LoginViewSet(viewsets.ViewSet):

    serializer_class = AuthTokenSerializer

    def create(self, request):
        return ObtainAuthToken().as_view()(request=request._request)
